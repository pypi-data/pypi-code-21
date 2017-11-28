# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import sys
import requests
import json
import uuid
from pkg_resources import resource_string
from ._constants import MMS_API_VERSION
from ._constants import MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES
from ._constants import MMS_IMAGE_URL_ENDPOINT
from ._constants import MMS_OPERATION_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import MLC_RESOURCE_ID_FMT
from ._constants import SUCCESS_RETURN_CODE
from ._model_management_account_util import get_current_model_management_url_base
from ._model_management_account_util import get_current_model_management_account
from ._ml_cli_error import MlCliError
from ._util import cli_context
from ._util import get_auth_header
from ._util import poll_mms_async_operation
from ._util import get_json
from ._util import get_paginated_results
from .manifest import _manifest_create


def image_create(image_name, image_description, manifest_id, driver_file, schema_file, dependencies,
                 runtime, requirements, conda_file, model_files, verb, context=cli_context):
    _image_create(image_name, image_description, manifest_id, driver_file, schema_file, dependencies,
                  runtime, requirements, conda_file, model_files, verb, context)


def _image_create(image_name, image_description, manifest_id, driver_file, schema_file, dependencies,
                  runtime, requirements, conda_file, model_files, verb, context):
    if verb:
        print('Starting image create')
    if not manifest_id and not driver_file:
        raise MlCliError('Either manifest id or information to create a manifest must be provided')

    mms_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    if not context.current_compute_name or not context.current_compute_resource_group or not context.current_compute_subscription_id:
        raise MlCliError('Missing information for current compute context. '
                         'Please set your current compute by running: '
                         'az ml env set -n <env_name> -g <env_rg>'.format(context.current_compute_name,
                                                                          context.current_compute_resource_group,
                                                                          context.current_compute_subscription_id))

    json_payload = json.loads(resource_string(__name__, 'data/mmsimagepayloadtemplate.json').decode('ascii'))
    json_payload['name'] = image_name
    json_payload['description'] = image_description
    json_payload['computeResourceId'] = MLC_RESOURCE_ID_FMT.format(context.current_compute_subscription_id,
                                                                   context.current_compute_resource_group,
                                                                   context.current_compute_name)

    if manifest_id:
        json_payload['manifestId'] = manifest_id
    else:
        json_payload['manifestId'] = _manifest_create(image_name, driver_file, None, schema_file, dependencies, runtime,
                                                      requirements, conda_file, None, model_files, verb, context)[1]

    if verb:
        print('Image payload: {}'.format(json_payload))

    try:
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code != 202:
        raise MlCliError('Error occurred creating image.', resp.headers, resp.content, resp.status_code)

    try:
        operation_location = resp.headers['Operation-Location']
    except KeyError:
        raise MlCliError('Invalid response header key: Operation-Location')
    create_operation_status_id = operation_location.split('/')[-1]

    if verb:
        print('Operation Id: {}'.format(create_operation_status_id))

    operation_url = get_current_model_management_url_base() + MMS_OPERATION_URL_ENDPOINT.format(create_operation_status_id)
    operation_headers = {'Authorization': auth_header}

    sys.stdout.write('Creating image')
    sys.stdout.flush()
    async_response = poll_mms_async_operation(operation_url, operation_headers, params,
                                              MMS_IMAGE_CREATE_OPERATION_POLLING_MAX_TRIES, context)
    if isinstance(async_response, tuple):
        try:
            error_contents = async_response[0]
            error_headers = async_response[1]

            status_code = error_contents['Error']['StatusCode']
            error_message = error_contents['Error']['Message']
            sub_id = context.current_compute_subscription_id
            mma_id = get_current_model_management_account()['id']
            request_id = error_headers['x-ms-client-request-id']
            image_id = error_contents['Id']
            if status_code >= 400 and status_code < 500:
                log_location = error_contents['Error']['Details'][0]['Message']
                raise MlCliError({'Error Message': error_message,
                                  'Log Information': log_location},
                                 error_headers, error_contents, status_code)
            elif status_code >= 500:
                raise MlCliError({'Error Message': error_message,
                                  'Additional information': {'Subscription ID': sub_id,
                                                             'Model Management Account ID': mma_id,
                                                             'Image ID': image_id,
                                                             'Request ID': request_id}},
                                 error_headers, error_contents, status_code)
        except MlCliError:
            raise
        except Exception:
            raise MlCliError('Error occurred', async_response[1], async_response[0])
    else:
        image_id = async_response

    print('Done.')
    print('Image ID: {}'.format(image_id))
    print('More details: \'az ml image show -i {}\''.format(image_id))
    print('Usage information: \'az ml image usage -i {}\''.format(image_id))
    return SUCCESS_RETURN_CODE, image_id


def image_show(image_id, verb, context=cli_context):
    _, result = _image_show(image_id, verb, context)
    return result, verb


def _image_show(image_id, verb, context):
    image_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT + '/{}'.format(image_id)
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', image_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        return SUCCESS_RETURN_CODE, get_json(resp.content, pascal=True)
    else:
        raise MlCliError('Error occurred while attempting to show image.', resp.headers, resp.content, resp.status_code)


def image_list(verb, context=cli_context):
    _, result = _image_list(verb, context)
    return result, verb


def _image_list(verb, context):
    image_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', image_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        return SUCCESS_RETURN_CODE, get_paginated_results(resp, headers, context)
    else:
        raise MlCliError('Error occurred while attempting to list images.',
                         resp.headers, resp.content, resp.status_code)


def image_usage(image_id, verb, context=cli_context):
   _image_usage(image_id, verb, context)


def _image_usage(image_id, verb, context):
    image_url = get_current_model_management_url_base() + MMS_IMAGE_URL_ENDPOINT + '/{}'.format(image_id)
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', image_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}'.format(image_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(image_url))

    if resp.status_code == 200:
        image = get_json(resp.content, pascal=True)
        try:
            image_location = image['ImageLocation']
        except KeyError:
            raise MlCliError('Error, unable to retrieve ImageLocation from response payload: {}'.format(image))
        try:
            compute_id = image['ComputeResourceId'].split('/')
            env_rg = compute_id[-5]
            env_name = compute_id[-1]
        except KeyError:
            raise MlCliError('Error, unable to retrieve ComputeResourceId from response payload: {}'.format(image))
        except IndexError:
            raise MlCliError('Error, unable to parse ComputeResourceId: {}'.format(compute_id))
        try:
            image_type = image['ImageType']
        except KeyError:
            raise MlCliError('Error, unable to retrieve ImageType from response payload: {}'.format(image))

        print('Service Creation Instructions:')
        print('    Run \'az ml service create realtime\' and provide the necessary information, including this image ID: {}'.format(image_id))
        print()
        if image_type == 'Docker':
            print('Docker Download Instructions:')
            print('    Run \'docker login\' with credentials obtained by running \'az ml env get-credentials -g {} -n {}\''.format(env_rg, env_name))
            print('        (If user name is not returned as a part of get-credentials, it is the part of your login server before the first period.)')
            print('    Run \'docker pull {}\' to pull the image down locally'.format(image_location))
        return SUCCESS_RETURN_CODE
    else:
        raise MlCliError('Error occurred while attempting to retrieve image information.',
                         resp.headers, resp.content, resp.status_code)
