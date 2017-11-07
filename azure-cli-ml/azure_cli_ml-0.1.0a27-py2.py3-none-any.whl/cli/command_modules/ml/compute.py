# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import requests
import socket
import subprocess
from ._util import cli_context
from ._ml_cli_error import MlCliError
from ._constants import SUCCESS_RETURN_CODE
from ._az_util import az_login
from ._az_util import az_check_subscription
from ._az_util import az_create_resource_group
from ._az_util import az_get_active_subscription_id
from ._az_util import az_install_kubectl
from ._az_util import az_get_provider
from ._compute_util import create_compute_resource
from ._compute_util import delete_compute_resource
from ._compute_util import get_compute_resource
from ._compute_util import get_current_compute_resource
from ._compute_util import get_compute_resource_keys
from ._compute_util import serialize_operationalization_cluster
from ._compute_util import ClusterType
from ._compute_util import __get_client
from ._az_util import az_register_provider
from ._k8s_util import check_for_kubectl
from azure.cli.core.commands import client_factory
from azure.mgmt.resource.resources import ResourceManagementClient
from msrestazure.azure_exceptions import CloudError
from ._constants import MLC_CLIENT_ENUMS_PATH
from importlib import import_module
mlc_client_enums = import_module(MLC_CLIENT_ENUMS_PATH, package=__package__)
OperationStatus = mlc_client_enums.OperationStatus

import azure.cli.core.azlogging as azlogging
logger = azlogging.get_az_logger(__name__)


def compute_create(cluster_name, service_principal_app_id, service_principal_password,
                   location, agent_count, agent_vm_size, resource_group=None, yes=False, cert_pem=None,
                   cert_key_pem=None, storage_arm_id=None, acr_arm_id=None, cert_cname=None, master_count=1,
                   cluster_type='local', context=cli_context, verb=False):
    _compute_create(resource_group, cluster_name, service_principal_app_id,
                    service_principal_password, location, agent_count, agent_vm_size, yes, cert_pem,
                    cert_key_pem, storage_arm_id, acr_arm_id, cert_cname, master_count, cluster_type, context, verb)

def _compute_create(resource_group, cluster_name, service_principal_app_id, service_principal_password,
                    location, agent_count, agent_vm_size, yes=False, cert_pem=None,
                    cert_key_pem=None, storage_arm_id=None, acr_arm_id=None, cert_cname=None, master_count=1,
                    cluster_type='local', context=cli_context, verb=False):
    if location is None:
        raise MlCliError('Location must be specified for environment creation.')

    if cluster_type != 'local' and master_count not in [1, 3, 5]:
        raise MlCliError('Master count must be 1, 3, or 5.')

    # handle SSL cert
    cert_str, key_str, ssl_enabled = None, None, 'Disabled'
    if cluster_type != 'local':
        if cert_pem is not None or cert_key_pem is not None or cert_cname is not None:
            if cert_key_pem is None:
                raise MlCliError('Certificate key file must be provided if certificate is provided.')
            if cert_pem is None:
                raise MlCliError('Certificate file must be provided if certificate key file is provided.')
            if cert_cname is None:
                raise MlCliError('Certificate CNAME must be provided if certificate is provided.')
            try:
                with open(cert_pem, 'r') as pemfile:
                    cert_str = pemfile.read()
            except (IOError, OSError) as exc:
                raise MlCliError("Error while reading certificate bytes", content=exc)
            try:
                with open(cert_key_pem, 'r') as keyfile:
                    key_str = keyfile.read()
            except (IOError, OSError) as exc:
                raise MlCliError("Error while reading certificate key bytes", content=exc)
            ssl_enabled = 'Enabled'

    # confirm user logged in
    az_login(yes=yes)

    # prompt user to confirm subscription
    az_check_subscription(yes=yes, context=context)

    # try to register before creating any resources
    try:
        mlc_rp = az_get_provider('Microsoft.MachineLearningCompute')
        if mlc_rp.registration_state.lower() != "registered":
            print(
                'Subscription is not registered for the Microsoft.MachineLearningCompute provider. Registering now...')
            try:
                az_register_provider('Microsoft.MachineLearningCompute')
            except CloudError as ce:
                raise MlCliError('Error registering subscription. '
                                 'Please contact the owner of this subscription to register the provider '
                                 'Microsoft.MachineLearningCompute.',
                                 content=ce)
    except CloudError:
        raise MlCliError('Failed to get registration state for the Microsoft.MachineLearningCompute provider.'
                         'Please contact your subscription owner to register the provider.')

    # if use passed storage acct ID, verify that it exists
    if storage_arm_id is not None:
        if verb:
            print('Validating passed storage: {}'.format(storage_arm_id))
        client = client_factory.get_mgmt_service_client(
            ResourceManagementClient).resources
        try:
            # raises CloudError if resource does not exist
            client.get_by_id(storage_arm_id, api_version='2017-06-01')
            active_sub_id = az_get_active_subscription_id().lower()
            storage_subscription = storage_arm_id.split('/')[2].lower()
            if active_sub_id != storage_subscription:
                raise MlCliError('Storage account must be in the same subscription as the '
                                 'compute. Target subscription: {}, storage subscription: '
                                 '{}'.format(active_sub_id, storage_subscription))
        except IndexError:
            # this shouldn't happen, as the check_existence call should throw CloudError
            raise MlCliError('Malformed storage ID: {}'.format(storage_arm_id))
        except CloudError as exc:
            raise MlCliError('Error validating storage with ID {}'.format(storage_arm_id), content=exc)

    if acr_arm_id is not None:
        if verb:
            print('Validating passed ACR: {}'.format(acr_arm_id))
        client = client_factory.get_mgmt_service_client(ResourceManagementClient).resources
        try:
            client.get_by_id(acr_arm_id, api_version='2017-10-01')
            active_sub_id = az_get_active_subscription_id().lower()
            acr_subscription = acr_arm_id.split('/')[2].lower()
            if active_sub_id != acr_subscription:
                raise MlCliError('ACR must be in the same subscription as the '
                                 'compute. Target subscription: {}, ACR subscription: '
                                 '{}'.format(active_sub_id, acr_subscription))
        except IndexError:
            # this shouldn't happen, as the check_existence call should throw CloudError
            raise MlCliError('Malformed ACR ID: {}'.format(acr_arm_id))
        except CloudError as exc:
            raise MlCliError('Error validating ACR with ID {}'.format(acr_arm_id), content=exc)

    # verify/create RG
    if resource_group is None:
        resource_group = az_create_resource_group(context, cluster_name, location=location)
    else:
        az_create_resource_group(context, resource_group, append='', location=location)

    if cluster_type == 'local':
        cluster_type = ClusterType.local
    else:
        from ._acs_util import validate_service_principal
        validate_service_principal(service_principal_app_id, service_principal_password)
        cluster_type = ClusterType.acs

    print('Provisioning compute resources...')
    # call MLCRP
    resp = create_compute_resource(resource_group, cluster_name, cluster_type, service_principal_app_id,
                                   service_principal_password, location, agent_count, agent_vm_size, cert_str,
                                   key_str, ssl_enabled, storage_arm_id, acr_arm_id, cert_cname,
                                   master_count)

    if verb:
        print('Create response\nStatus Code: {}\nHeaders: {}\nContent: {}'.format(resp.status_code, resp.headers, resp.content))

    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise MlCliError('Received bad response from MLC RP', resp.headers, resp.content, resp.status_code)

    print('Resource creation submitted successfully.')
    if cluster_type != ClusterType.local:
        print('Resources may take 10-20 minutes to be completely provisioned.')
        print('To see if your environment is ready to use, run:')
    else:
        print('To see more information for your environment, run:')
    print('  az ml env show -g {} -n {}'.format(resource_group, cluster_name))
    if cluster_type != ClusterType.local:
        print('Once your environment has successfully provisioned, you can set it as your target context using:')
    else:
        print('You can set the new environment as your target context using:')
    print('  az ml env set -g {} -n {}'.format(resource_group, cluster_name))
    return SUCCESS_RETURN_CODE


def compute_delete(resource_group, cluster_name, context=cli_context):
    """
    Delete an MLCRP-provisioned resource.
    :param resource_group:
    :param cluster_name:
    :param context:
    :return:
    """
    _compute_delete(resource_group, cluster_name, context)


def _compute_delete(resource_group, cluster_name, context=cli_context):
    resp = delete_compute_resource(resource_group, cluster_name)
    try:
        resp.raise_for_status()
    except requests.exceptions.HTTPError:
        raise MlCliError('Received bad response from MLC RP', resp.headers, resp.content, resp.status_code)
    print('Resource deletion successfully submitted.')
    print('Resources may take 1-2 minutes to be completely deprovisioned.')
    return SUCCESS_RETURN_CODE


def compute_set(resource_group, cluster_name, context=cli_context, disable_dashboard=False):
    """
    Set the active MLC environment.
    :param resource_group:
    :param cluster_name:
    :param context:
    :return:
    """
    _compute_set(resource_group, cluster_name, context, disable_dashboard)


def _compute_set(resource_group, cluster_name, context, disable_dashboard=False):
    compute_resource = get_compute_resource(resource_group, cluster_name)
    state = compute_resource['provisioning_state'].strip()
    if state.lower() != OperationStatus.succeeded.name.lower():
        raise MlCliError('Resource with group {} and name {} cannot be set, '
                         'as its provisioning state is {}. Provisioning state {} '
                         'is required.'.format(resource_group, cluster_name, state, OperationStatus.succeeded.name))
    context.set_compute(compute_resource)
    try:
        executable = 'kubectl' if context.os_is_unix() else 'kubectl.exe'
        full_install_path = os.path.join(os.path.expanduser('~'), 'bin', executable)
        os.environ['PATH'] += os.pathsep + os.path.dirname(full_install_path)
        context.check_output('kubectl')
    except (subprocess.CalledProcessError, OSError, IOError):
        az_install_kubectl(context)
    if not context.in_local_mode() and not disable_dashboard:
        _start_kubectl_proxy(resource_group, cluster_name, context)
    print('Compute set to {}.'.format(context.current_compute_name))
    return SUCCESS_RETURN_CODE


def compute_show(resource_group=None, cluster_name=None, verb=False, context=cli_context):
    """
    Show an MLC resource; If resource_group or cluster_name are not provided, shows the
    active MLC env.
    :param resource_group:
    :param cluster_name:
    :param verb:
    :param context:
    :return:
    """
    _, result = _compute_show(resource_group, cluster_name, context)
    return result, verb


def _compute_show(resource_group, cluster_name, context):
    if resource_group is None or cluster_name is None:
        compute = get_current_compute_resource(context)
        compute['current_execution_mode'] = context.current_execution_mode
    else:
        compute = get_compute_resource(resource_group, cluster_name)
        del(compute['current_execution_mode'])

    return SUCCESS_RETURN_CODE, compute


def compute_list(resource_group, verb=False, context=cli_context):
    """
    List all environments in the current subscription. Filters by resource_group if provided
    :param resource_group:
    :param verb: 
    :param context: 
    :return: 
    """
    _, result = _compute_list(resource_group, verb, context)
    return result, verb


def _compute_list(resource_group, verb, context):
    client = __get_client()
    if resource_group:
        result = client.list_by_resource_group(resource_group)
    else:
        result = client.list_by_subscription_id()

    envs = []
    for env in result:
        envs.append(serialize_operationalization_cluster(env))
    return SUCCESS_RETURN_CODE, envs


def get_credentials(resource_group, cluster_name, install_kube_config, verb, context=cli_context):
    """
    List the keys for an environment.
    :param resource_group:
    :param cluster_name:
    :param install_kube_config:
    :param verb:
    :param context:
    :return:
    """
    return _get_credentials(resource_group, cluster_name, install_kube_config, verb, context)[1]


def _get_credentials(resource_group, cluster_name, install_kube_config, verb, context):
    result = get_compute_resource_keys(resource_group, cluster_name)

    if not context.in_local_mode():
        # with nargs='?', when the flag appears but no arg appears, the value is None
        # when the flag does not appear, the value is '' (default)
        if install_kube_config is None:
            context.current_compute_creds = result
            context.update_kube_config()
        elif install_kube_config:
            try:
                with open(install_kube_config, 'w') as kube_config:
                    kube_config.write(result.container_service.acs_kube_config)
            except (OSError, IOError) as exc:
                raise MlCliError('Error occurred attempting to update kube config file.', content=exc)

    return SUCCESS_RETURN_CODE, result


def _start_kubectl_proxy(resource_group, cluster_name, context):
    _get_credentials(resource_group, cluster_name, install_kube_config=None, verb=False, context=context)
    FNULL = open(os.devnull, 'w')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('', 0))
    local_port = sock.getsockname()[1]
    sock.close()
    if not check_for_kubectl(context):
        return
    subprocess.Popen(["kubectl", "proxy", "--port={}".format(local_port)], stdout=FNULL)
    dashboard_endpoint = '127.0.0.1:{}/ui'.format(local_port)
    print('Kubectl dashboard started for cluster at this endpoint: {}'.format(dashboard_endpoint))
