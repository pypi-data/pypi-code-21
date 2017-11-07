# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import requests
import json
from pkg_resources import resource_string
from uuid import UUID
from .service._realtimeutilities import upload_dependency
from ._constants import MMS_API_VERSION
from ._constants import MMS_MODEL_URL_ENDPOINT
from ._constants import MMS_SYNC_TIMEOUT_SECONDS
from ._constants import SUCCESS_RETURN_CODE
from ._model_management_account_util import get_current_model_management_url_base
from ._ml_cli_error import MlCliError
from ._util import cli_context
from ._util import get_auth_header
from ._util import get_json
from ._util import get_paginated_results


def model_register(model_path, model_name, tags, description, verb, context=cli_context):
    _model_register(model_path, model_name, tags, description, verb, context)


def _model_register(model_path, model_name, tags, description, verb, context):
    if verb:
        print('Starting model register')
    unpack, model_url, filename = upload_dependency(context, model_path, verb)
    if unpack < 0:
        raise MlCliError('Error resolving model: no such file or directory {}'.format(model_path))
    auth_token = get_auth_header()
    headers = {'Content-Type': 'application/json', 'Authorization': auth_token}
    params = {'api-version': MMS_API_VERSION}

    json_payload = json.loads(resource_string(__name__, 'data/mmsmodelpayloadtemplate.json').decode('ascii'))
    json_payload['name'] = model_name
    json_payload['url'] = model_url
    json_payload['unpack'] = unpack == 1
    if tags:
        json_payload['tags'] = tags
    if description:
        json_payload['description'] = description
    mms_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT

    if verb:
        print('Attempting to register model to {}'.format(mms_url))
        print('Attempting to register model with this information: {}'.format(json_payload))

    try:
        if verb:
            print('Model register post url: {}'.format(mms_url))
        resp = context.http_call('post', mms_url, params=params, headers=headers, json=json_payload, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}.'.format(mms_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(mms_url))

    if resp.status_code == 200:
        print('Successfully registered model')
        model = get_json(resp.content, pascal=True)
        try:
            print('Id: {}'.format(model['Id']))
            print('More information: \'az ml model show -m {}\''.format(model['Id']))
            return SUCCESS_RETURN_CODE, model['Id']
        except KeyError:
            raise MlCliError('Invalid model key: Id')
    else:
        raise MlCliError('Error occurred registering model.', resp.headers, resp.content, resp.status_code)


def model_show(model, tag, verb, context=cli_context):
    _, result = _model_show(model, tag, verb, context)
    return result, verb

def _model_show(model, tag, verb, context):
    model_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT
    auth_token = get_auth_header()
    headers = {'Authorization': auth_token}
    params = {'api-version': MMS_API_VERSION}

    try:
        # If the model is a valid uuid4, then the ID has been provided
        UUID(model, version=4)
        model_id = model
        model_name = None
        if verb:
            print('Model {} successfully parsed into ID'.format(model))
    except ValueError:
        # If the model is not a valid uuid4, then the name has been provided
        model_name = model
        model_id = None
        if verb:
            print('Model {} parsed into name'.format(model))

    if model_name:
        params['name'] = model_name
    elif model_id:
        model_url += '/{}'.format(model_id)
    else:
        raise MlCliError('Error attempting to parse model: {}'.format(model))
    if tag:
        params['tag'] = tag

    try:
        resp = context.http_call('get', model_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        if model_name:
            result = get_paginated_results(resp, headers, context)
        else:
            result = get_json(resp.content, pascal=True)
        return SUCCESS_RETURN_CODE, result
    else:
        raise MlCliError('Error occurred showing model.', resp.headers, resp.content, resp.status_code)


def model_list(tag, verb, context=cli_context):
    _, result = _model_list(tag, verb, context)
    return result, verb


def _model_list(tag, verb, context):
    model_url = get_current_model_management_url_base() + MMS_MODEL_URL_ENDPOINT
    auth_token = get_auth_header()
    params = {'api-version': MMS_API_VERSION}
    
    headers = {'Authorization': auth_token}

    if tag:
        params['tag'] = tag

    try:
        resp = context.http_call('get', model_url, params=params, headers=headers, timeout=MMS_SYNC_TIMEOUT_SECONDS)
    except requests.ConnectionError:
        raise MlCliError('Error connecting to {}.'.format(model_url))
    except requests.Timeout:
        raise MlCliError('Error, request to {} timed out.'.format(model_url))

    if resp.status_code == 200:
        return SUCCESS_RETURN_CODE, get_paginated_results(resp, headers, context)
    else:
        raise MlCliError('Error occurred listing models.', resp.headers, resp.content, resp.status_code)
