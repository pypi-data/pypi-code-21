# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------
import json
import os
from azure.cli.core.commands.client_factory import get_mgmt_service_client
from ._constants import MMS_MODEL_MANAGEMENT_ACCOUNT_PROFILE
from ._ml_cli_error import MlCliError


def get_service_client():
    from azure.cli.command_modules.ml._mma import AzureMachineLearningModelManagementAccount
    return get_mgmt_service_client(AzureMachineLearningModelManagementAccount).model_management_accounts


def get_config_dir():
    return os.getenv('AZURE_CONFIG_DIR', os.path.expanduser(os.path.join('~', '.azure')))


def get_current_model_management_account():
    azure_folder = get_config_dir()
    model_management_account_file = os.path.join(azure_folder, MMS_MODEL_MANAGEMENT_ACCOUNT_PROFILE)

    if not os.path.isfile(model_management_account_file):
        raise MlCliError('Model Management Account not set. Please run \'az ml account modelmanagement set\'')

    with open(model_management_account_file, 'r') as ha_file:
        try:
            model_management_account = json.load(ha_file)
        except ValueError as e:
            os.remove(model_management_account_file)
            raise MlCliError('Error retrieving currently set Model Management Account: invalid JSON. '
                             'Please run \'az ml account modelmanagement set\'')

    return model_management_account


def serialize_model_management_account(model_management_account_client, model_management_account):
    """
    Need to manually serialize the pieces of the model management account because the client's serializer ignores read-only members
    :param model_management_account_client: 
    :param model_management_account: 
    :return: 
    """
    serialized_model_management_account = {}
    for attr, key_type_map in model_management_account._attribute_map.items():
        orig_attr = getattr(model_management_account, attr)
        attr_type = key_type_map['type']
        serialized_model_management_account[attr] = model_management_account_client._serialize._serialize(orig_attr, attr_type)
    model_management_account_details = model_management_account.id.split('/')
    serialized_model_management_account['subscription'] = model_management_account_details[2]
    serialized_model_management_account['resource_group'] = model_management_account_details[4]

    return serialized_model_management_account


def handle_error_response_exception(exception):
    """
    Currently the HA SDK can return two different types of exceptions, one from ARM and one from the RP. The ones
    from the RP are deserialized into the ErrorResponse class, which contains a details attribute. This is checked in
    the if statement and used if present. The ARM exception cannot be deserialized into the class, and as such
    error.details is none. In this case, we get the useful information from the exception response itself, in the
    else case.
    :param exception: 
    :return: 
    """
    try:
        if exception.error.details:
            return exception.error.details[0].code, exception.error.details[0].message
        else:
            exception_content = exception.response.json()
            try:
                return exception_content['error']['code'], exception_content['error']['message']
            except KeyError:
                raise MlCliError('Invalid exception response key.', content=exception_content)
    except AttributeError:
        raise MlCliError('Invalid attribute \'error\' in exception', content=exception)


def get_current_model_management_url_base():
    model_management_account = get_current_model_management_account()
    mms_swagger_location = model_management_account['model_management_swagger_location']
    return mms_swagger_location.rsplit('/', 1)[0]
