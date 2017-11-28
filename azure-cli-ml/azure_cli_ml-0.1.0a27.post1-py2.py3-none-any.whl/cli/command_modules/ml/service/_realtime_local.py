# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import docker
import requests
import sys
import time
from ._docker_utils import get_docker_client
from ._realtimeutilities import get_local_realtime_service_port
from ._realtimeutilities import get_sample_data
from ._realtimeutilities import get_local_webservices
from ._realtimeutilities import get_container
from .._constants import APP_INSIGHTS_URL
from .._constants import DEFAULT_INPUT_DATA
from .._constants import SCORING_URI_FORMAT
from .._constants import SUCCESS_RETURN_CODE
from .._constants import SWAGGER_URI_FORMAT
from .._constants import HEALTH_URI_FORMAT
from .._constants import LOCAL_HEALTH_CHECK_POLLING_MAX_TRIES
from .._constants import LOCAL_HEALTH_CHECK_POLLING_INTERVAL_SECONDS
from ..image import _image_show
from .._get_logs import get_logs_from_docker
from .._ml_cli_error import MlCliError


def local_service_create(service_name, image_id, app_insights_logging_enabled, model_data_collection_enabled, verb, context):
    """Deploy a realtime web service locally as a docker container."""

    result, image_details = _image_show(image_id, verb, context)
    if result != SUCCESS_RETURN_CODE:
        raise MlCliError('Error, unable to retrieve information for {}.'.format(image_id))
    try:
        image_location = image_details['ImageLocation']
    except KeyError:
        raise MlCliError({'Message': 'Error, unable to determine ImageLocation', 'Image Details': image_details})
    if app_insights_logging_enabled is None:
        app_insights_logging_enabled = False
    if model_data_collection_enabled is None:
        model_data_collection_enabled = False
    app_insights_logging_enabled = str(app_insights_logging_enabled).lower()
    model_data_collection_enabled = str(model_data_collection_enabled).lower()

    print("[Local mode] Running docker container.")

    client = get_docker_client(verb)
    try:
        print('[Local mode] Pulling the image from {}. '
              'This may take a few minutes, depending on your connection speed...'.format(image_location))
        sys.stdout.write('[Local mode] Pulling')
        num_lines = 0
        for outer_line in client.api.pull(image_location, stream=True, auth_config={
            'username': context.acr_user,
            'password': context.acr_pw
        }):
            # stream sometimes sends multiple lines as one "line," despite documentation
            num_lines += outer_line.decode().count('\n')
            while num_lines > 10:
                sys.stdout.write('.')
                sys.stdout.flush()
                num_lines -= 10
        print('')
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to pull image {}'.format(image_location), content=exc)
    container_env = {'AML_APP_INSIGHTS_KEY': context.app_insights_account_key,
                     'AML_APP_INSIGHTS_ENABLED': app_insights_logging_enabled,
                     'AML_MODEL_DC_STORAGE_ENABLED': model_data_collection_enabled,
                     'AML_MODEL_DC_EVENT_HUB_ENABLED': 'false',
                     'AML_MODEL_DC_STORAGE': context.model_dc_storage,
                     'AML_MODEL_DC_EVENT_HUB': context.model_dc_event_hub}
    container_labels = {'amlid': service_name}
    if app_insights_logging_enabled == 'true':
        container_labels['compute_sub'] = context.current_compute_subscription_id
        container_labels['compute_rg'] = context.current_compute_resource_group
        container_labels['app_insights_id'] = context.app_insights_account_id
    try:
        client.containers.run(image_location,
                              environment=container_env,
                              detach=True,
                              publish_all_ports=True,
                              labels=container_labels)
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to start container', content=exc)

    # above container does not contain full port info--fetch it
    try:
        dockerport = get_local_realtime_service_port(service_name, verb)
    except MlCliError as exc:
        raise MlCliError('[Local mode] Failed to start container. '
                         'Please report this to deployml@microsoft.com with your image id: {}'.format(image_location),
                         content=exc.to_json())

    # Wait for the in container server to boot up before making a call for sample data
    time.sleep(10)
    sys.stdout.write('[Local mode] Waiting for container to initialize')
    sys.stdout.flush()
    health_url = HEALTH_URI_FORMAT.format('http://127.0.0.1:{}'.format(dockerport))
    health_check_iteration = 0
    while health_check_iteration < LOCAL_HEALTH_CHECK_POLLING_MAX_TRIES:
        try:
            result = context.http_call('get', health_url, timeout=20)
        except requests.ConnectionError:
            raise MlCliError('Error, container failed to initialize. '
                             'Please run \'az ml service logs realtime -i {}\' to determine the cause.'.format(service_name))
        except requests.Timeout:
            time.sleep(LOCAL_HEALTH_CHECK_POLLING_INTERVAL_SECONDS)
            sys.stdout.write('.')
            sys.stdout.flush()
            health_check_iteration += 1
            continue

        if result.status_code == 200:
            break
        elif result.status_code == 502:
            time.sleep(LOCAL_HEALTH_CHECK_POLLING_INTERVAL_SECONDS)
            sys.stdout.write('.')
            sys.stdout.flush()
            health_check_iteration += 1
            continue
        else:
            raise MlCliError('Error, container failed to initialize '
                             'Please run \'az ml service logs realtime -i {}\' to determine the cause.'.format(service_name))
    if health_check_iteration == LOCAL_HEALTH_CHECK_POLLING_MAX_TRIES:
        raise MlCliError('Error, check for container initialization timed out '
                         'Please run \'az ml service logs realtime -i {}\' to determine the cause.'.format(service_name))
    swagger_url = SWAGGER_URI_FORMAT.format('http://127.0.0.1:{}'.format(dockerport))
    input_data = get_sample_data(swagger_url, verbose=verb)
    if not input_data:
        input_data = DEFAULT_INPUT_DATA
    print('')
    print('[Local mode] Done')
    print('[Local mode] Service ID: {}'.format(service_name))
    if context.os_is_unix():
        print('[Local mode] Usage: az ml service run realtime -i {} -d {}'.format(service_name, input_data))
    else:
        print('[Local mode] Usage for cmd: az ml service run realtime -i {} -d {}'.format(service_name, input_data))
        print('[Local mode] Usage for powershell: az ml service run realtime -i {} --% -d {}'.format(service_name, input_data))
    print('[Local mode] Additional usage information: \'az ml service usage realtime -i {}\''.format(service_name))

    if app_insights_logging_enabled == 'true':
        try:
            app_insights_id = context.current_env['app_insights']['resourceId'].split('/')[-1]
            print('[Local mode] App insights logs can be found here: {}'.format(
                APP_INSIGHTS_URL.format(
                    context.current_compute_subscription_id, context.current_compute_resource_group, app_insights_id)))
        except:
            pass
    return SUCCESS_RETURN_CODE, service_name


def local_service_run(service_name, input_data, verb, context):
    """Run a previously published local realtime web service."""

    try:
        container_port = get_local_realtime_service_port(service_name, verb)
    except MlCliError as exc:
        raise MlCliError('[Local mode] No service named {} found running locally.'.format(service_name), content=exc.to_json())
    else:
        headers = {'Content-Type': 'application/json'}
        if input_data == '':
            print("No input data specified. Checking for sample data.")
            swagger_url = SWAGGER_URI_FORMAT.format("http://127.0.0.1:{}".format(container_port))
            sample_data = get_sample_data(swagger_url, headers, verb)
            if sample_data:
                input_data = sample_data
                print('Using sample data: ' + input_data)
        else:
            if verb:
                print('[Debug] Input data is {}'.format(input_data))
                print('[Debug] Input data type is {}'.format(type(input_data)))

        service_url = 'http://127.0.0.1:{}/score'.format(container_port)
        if verb:
            print("Service url: {}".format(service_url))
        try:
            result = requests.post(service_url, headers=headers, data=input_data, verify=False, timeout=20)
        except requests.ConnectionError:
            print('[Local mode] Error connecting to container. Please try recreating your local service.')
            return

        if verb:
            print(result.content)

        if result.status_code == 200:
            result = result.json()
            print(result)
            return SUCCESS_RETURN_CODE
        else:
            content = result.content.decode()
            if content == "ehostunreach":
                print('Error scoring the service.')
                raise MlCliError('Unable to reach the requested host. '
                                 'If you just created this service, it may not be available yet. '
                                 'Please try again in a few minutes.')
            raise MlCliError('Error occurred while attempting to score service {}.'.format(service_name),
                             result.headers, result.content, result.status_code)


def local_service_delete(service_name, verbose, context):
    """Delete a locally published realtime web service."""
    client = get_docker_client(verbose)
    try:
        containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to list containers', content=exc)
    if not containers:
        raise MlCliError('[Local mode] Error: no service named {} found running locally.'.format(service_name))
    if len(containers) != 1:
        raise MlCliError("[Local mode] Error: ambiguous reference - too many containers ({}) with the same label.".format(len(containers)))
    container = containers[0]
    container_id = container.attrs['Id'][0:12]
    if verbose:
        print("Killing docker container id {}".format(container_id))
    image_name = container.attrs['Config']['Image']
    try:
        container.kill()
        container.remove()
        client.images.remove(image_name, force=True)
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to properly remove service', content=exc)
    print("Service deleted.")
    return SUCCESS_RETURN_CODE


# TODO Update this
def local_service_list(verb, context):
    return SUCCESS_RETURN_CODE, get_local_webservices(verb=verb, context=context)


def local_service_show(service_name, verb, context):
    services = get_local_webservices(service_name, verb, context)

    if len(services) == 0:
        service = None
    else:
        service = services[0]
    return SUCCESS_RETURN_CODE, service


def local_service_usage(service_name, verb, context):
    client = get_docker_client(verb)
    try:
        containers = client.containers.list(filters={'label': 'amlid={}'.format(service_name)})
    except docker.errors.DockerException as exc:
        raise MlCliError('Unable to list containers', content=exc)

    if len(containers) != 1:
        raise MlCliError('[Local mode] Error retrieving container details. '
                         'Label should match exactly one container and instead matched {}.'.format(len(containers)))
    container = containers[0]
    ports = container.attrs['NetworkSettings']['Ports']
    scoring_port_key = [x for x in ports.keys() if '5001' in x]
    if len(scoring_port_key) != 1:
        raise MlCliError('[Local mode] Error: Malconfigured container. Cannot determine scoring port.')
    scoring_port = ports[scoring_port_key[0]][0]['HostPort']
    if scoring_port:
        service_host = 'http://127.0.0.1:' + str(scoring_port)
        scoring_url = SCORING_URI_FORMAT.format(service_host)
        swagger_url = SWAGGER_URI_FORMAT.format(service_host)
        try:
            app_insights_url = APP_INSIGHTS_URL.format(container.attrs['Config']['Labels']['compute_sub'],
                                                       container.attrs['Config']['Labels']['compute_rg'],
                                                       container.attrs['Config']['Labels']['app_insights_id'])
        except KeyError:
            app_insights_url = None
    else:
        raise MlCliError('[Local mode] Error: Misconfigured container. Cannot determine scoring port.')

    return scoring_url, swagger_url, app_insights_url


def local_service_logs(service_name, request_id, verb):
    if not service_name:
        raise MlCliError('Error, service name required for local services.')
    container_name = get_container(service_name, all=True, verb=verb)
    if container_name:
        get_logs_from_docker(container_name, requestId=request_id, verb=verb)
        return SUCCESS_RETURN_CODE
