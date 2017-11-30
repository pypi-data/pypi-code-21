# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import os
import requests
import json
from pkg_resources import resource_string
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_API_VERSION
from ._constants import MMS_MANIFEST_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._manifest_util import handle_driver_file
from ._manifest_util import handle_model_files
from ._manifest_util import upload_runtime_properties_file
from ._model_management_account_util import get_current_model_management_url_base
from ._ml_cli_error import MlCliError
from ._util import cli_context
from ._util import get_auth_header
from ._util import get_json
from ._util import add_sdk_to_requirements
from ._util import wrap_driver_file
from ._util import get_paginated_results
from ._constants import SUPPORTED_RUNTIMES


def manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                    conda_file, model_ids, model_files, verb, context=cli_context):
    _manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                     conda_file, model_ids, model_files, verb, context)


def _manifest_create(manifest_name, driver_file, manifest_description, schema_file, dependencies, runtime, requirements,
                     conda_file, model_ids, model_files, verb, context):
    if verb:
        print('Starting manifest create')
    mms_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    # The driver file must be in the current directory
    driver_file_path = os.path.abspath(os.path.dirname(driver_file))
    if not os.getcwd() == driver_file_path:
        raise MlCliError('Unable to use a driver file not in current directory. '
                         'Please navigate to the location of the driver file and try again.')

    json_payload = json.loads(resource_string(__name__, 'data/mmsmanifestpayloadtemplate.json').decode('ascii'))
    json_payload['name'] = manifest_name
    json_payload['description'] = manifest_description
    if not runtime:
        raise MlCliError('Missing runtime. Possible runtimes are: {}'.format('|'.join(SUPPORTED_RUNTIMES.keys())))
    elif runtime in SUPPORTED_RUNTIMES.keys():
        json_payload['targetRuntime']['runtimeType'] = SUPPORTED_RUNTIMES[runtime]
    else:
        raise MlCliError('Provided runtime not supported. '
                         'Possible runtimes are: {}'.format('|'.join(SUPPORTED_RUNTIMES.keys())))

    if requirements:
        requirements = requirements.rstrip(os.sep)
    if conda_file:
        conda_file = conda_file.rstrip(os.sep)
    # add SDK to requirements file
    requirements = add_sdk_to_requirements(requirements)

    if requirements:
        if verb:
            print('Uploading {} file'.format('pipRequirements'))
        json_payload['targetRuntime']['properties']['pipRequirements'] = upload_runtime_properties_file(requirements, context)
    if conda_file:
        if verb:
            print('Uploading {} file'.format('condaEnvFile'))
        json_payload['targetRuntime']['properties']['condaEnvFile'] = upload_runtime_properties_file(conda_file, context)

    if not model_files and not model_ids:
        print("No model information provided, skipping model creation")
        model_info = None
    else:
        model_info = handle_model_files(model_ids, model_files, verb, context)

    if model_info:
        json_payload['modelIds'] = model_info

    driver_file = driver_file.rstrip(os.sep)
    if schema_file:
        schema_file_path = os.path.abspath(os.path.dirname(schema_file))
        common_prefix = os.path.commonprefix([driver_file_path, schema_file_path])
        if not common_prefix == driver_file_path:
            raise MlCliError('Schema file must be in the same directory as the driver file, or in a subdirectory.')
        schema_file = schema_file.rstrip(os.sep)
    driver_file_name, driver_file_extension = os.path.splitext(driver_file)
    if driver_file_extension == '.py':
        driver_mime_type = 'application/x-python'

        # wrap user driver
        wrapped_driver_file = wrap_driver_file(driver_file, schema_file, dependencies)
    else:
        raise MlCliError('Invalid driver type. Currently only Python drivers are supported.')
    driver_package_location = handle_driver_file(wrapped_driver_file, verb, context)
    json_payload['assets'].append({'id': 'driver', 'url': driver_package_location, 'mimeType': driver_mime_type})

    if schema_file:
        dependencies.append(schema_file)

    for dependency in dependencies:
        (status, location, filename) = upload_dependency(context, dependency, verb)
        if status < 0:
            raise MlCliError('Error resolving dependency: no such file or directory {}'.format(dependency))
        else:
            # Add the new asset to the payload
            new_asset = {'mimeType': 'application/octet-stream',
                         'id': filename[:32],
                         'url': location,
                         'unpack': status == 1}
            json_payload['assets'].append(new_asset)
            if verb:
                print("Added dependency {} to assets.".format(dependency))

    if verb:
        print('Manifest payload: {}'.format(json_payload))

    try:
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code == 200:
        print('Successfully created manifest')
        manifest = get_json(resp.content, pascal=True)
        try:
            print('Id: {}'.format(manifest['Id']))
            print('More information: \'az ml manifest show -i {}\''.format(manifest['Id']))
            return SUCCESS_RETURN_CODE, manifest['Id']
        except KeyError:
            raise MlCliError('Invalid manifest key: Id')
    else:
        raise MlCliError('Error occurred creating manifest.', resp.headers, resp.content, resp.status_code)


def manifest_show(manifest_id, verb, context=cli_context):
    _, result = _manifest_show(manifest_id, verb, context)
    return result, verb


def _manifest_show(manifest_id, verb, context):
    manifest_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT + '/{}'.format(manifest_id)
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', manifest_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}'.format(manifest_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(manifest_url))

    if resp.status_code == 200:
        return SUCCESS_RETURN_CODE, get_json(resp.content, pascal=True)
    else:
        raise MlCliError('Error occurred while attempting to show manifest.',
                         resp.headers, resp.content, resp.status_code)


def manifest_list(verb, context=cli_context):
    _, result = _manifest_list(verb, context)
    return result, verb


def _manifest_list(verb, context):
    manifest_url = get_current_model_management_url_base() + MMS_MANIFEST_URL_ENDPOINT
    auth_header = get_auth_header()
    headers = {'Authorization': auth_header}
    params = {'api-version': MMS_API_VERSION}

    try:
        resp = context.http_call('get', manifest_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}'.format(manifest_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(manifest_url))

    if resp.status_code == 200:
        return SUCCESS_RETURN_CODE, get_paginated_results(resp, headers, context)
    else:
        raise MlCliError('Error occurred while attempting to list manifests.',
                         resp.headers, resp.content, resp.status_code)
