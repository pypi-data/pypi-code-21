# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#pylint: disable=line-too-long

from azure.cli.core.commands import client_factory
from ._constants import MLC_MODELS_PATH
from ._constants import MLC_CLIENT_PATH
from importlib import import_module
from azure.cli.core.util import CLIError
from azure.cli.command_modules.ml.commands_utility import load_commands
from azure.cli.command_modules.ml.all_parameters import register_command_arguments
from msrestazure.azure_exceptions import CloudError
from ._transformers import transform_mlc_resource
from ._transformers import transform_mlc_resource_list
from ._transformers import transform_mma_show
from ._transformers import table_transform_mma_show
from ._transformers import transform_mma_list
from ._transformers import table_transform_mma_list
from ._transformers import transform_model_show
from ._transformers import table_transform_model_show
from ._transformers import transform_model_list
from ._transformers import table_transform_model_list
from ._transformers import transform_manifest_show
from ._transformers import table_transform_manifest_show
from ._transformers import transform_manifest_list
from ._transformers import table_transform_manifest_list
from ._transformers import transform_image_show
from ._transformers import table_transform_image_show
from ._transformers import transform_image_list
from ._transformers import table_transform_image_list
from ._transformers import transform_service_show
from ._transformers import table_transform_service_show
from ._transformers import transform_service_list
from ._transformers import table_transform_service_list

# Every command has several parts:
#
# 1. Commands [Add your command to ALL_COMMANDS so that it gets added. Optional arguments for
# registration (such as table_transformer) that must be provided to "cli_command" should be
# included as part of the dictionary in ALL_COMMANDS. Otherwise, add an empty dictionary.]
#
# 2. Command Information [Create a new key for your command in command_details.json.
# This will contain its name, the command itself, the command function/pointer, and arguments.]
#
# 3. Arguments [Should be added as part of the command_details.json file. See other commands for examples.]
#
# 4. Module [Functions called by the commands, make sure to specify their name when
# creating the command.]
#
# 5. Help [Warning: Help is not in this file! Make sure to update _help.py,
# which is under the same directory, with the new commands.]

mlc_client = import_module(MLC_CLIENT_PATH, package=__package__)
MachineLearningComputeManagementClient = mlc_client.MachineLearningComputeManagementClient

mlc_models = import_module(MLC_MODELS_PATH, package=__package__)
ErrorResponseWrapperException = mlc_models.ErrorResponseWrapperException
ErrorResponse = mlc_models.ErrorResponse


def _handle_exceptions(exc):
    """
    :param exc: Exception thrown by AML CLI
    :raises CLIError
    """
    if isinstance(exc, CLIError):
        raise exc
    elif isinstance(exc, ErrorResponseWrapperException):
        try:
            exc_to_process = exc.error.error
            if exc_to_process is not None and exc_to_process.details is not None:
                exc_to_process = exc_to_process.details[0]
            raise CLIError('{}: {}'.format(exc_to_process.code,
                                           exc_to_process.message))
        except CLIError:
            raise
        except:
            print('Failed to parse inner exception correctly.')
            print('type(exc): {}'.format(type(exc)))
            print('type(exc.error): {}'.format(type(exc.error)))
            pass
    elif isinstance(exc, CloudError):
        raise CLIError(exc)

    # ValidationError gets here, but prints nicely
    raise CLIError(exc)


ALL_COMMANDS = {
    # "ml service create batch": {"formatter_class": AmlHelpFormatter},
    # "ml service run batch": {"formatter_class": AmlHelpFormatter},
    # "ml service list batch": {},
    # "ml service show batch": {},
    # "ml service delete batch": {},
    # "ml service showjob batch": {},
    # "ml service listjobs batch": {},
    # "ml service canceljob batch": {},

    "ml env local": {},
    "ml env cluster": {},
    "ml env show": {"exception_handler": _handle_exceptions, "transform": transform_mlc_resource},
    "ml env setup": {"exception_handler": _handle_exceptions},
    "ml env list": {"exception_handler": _handle_exceptions, "transform": transform_mlc_resource_list},
    "ml env delete": {'exception_handler': _handle_exceptions},
    "ml env set": {'exception_handler': _handle_exceptions},
    "ml env get-credentials": {"exception_handler": _handle_exceptions},

    "ml service create realtime": {},
    "ml service list realtime": {"transform": transform_service_list, "table_transformer": table_transform_service_list},
    "ml service show realtime": {"transform": transform_service_show, "table_transformer": table_transform_service_show},
    "ml service delete realtime": {},
    "ml service run realtime": {},
    "ml service update realtime": {},
    'ml service keys realtime': {},
    'ml service usage realtime': {},
    'ml service logs realtime': {},

    "ml model register": {},
    "ml model show": {"transform": transform_model_show, "table_transformer": table_transform_model_show},
    "ml model list": {"transform": transform_model_list, "table_transformer": table_transform_model_list},

    "ml manifest create": {},
    "ml manifest show": {"transform": transform_manifest_show, "table_transformer": table_transform_manifest_show},
    "ml manifest list": {"transform": transform_manifest_list, "table_transformer": table_transform_manifest_list},

    "ml image create": {},
    "ml image show": {"transform": transform_image_show, "table_transformer": table_transform_image_show},
    "ml image list": {"transform": transform_image_list, "table_transformer": table_transform_image_list},
    "ml image usage": {},

    "ml account modelmanagement create": {},
    "ml account modelmanagement show": {"transform": transform_mma_show, "table_transformer": table_transform_mma_show},
    "ml account modelmanagement list": {"transform": transform_mma_list, "table_transformer": table_transform_mma_list},
    "ml account modelmanagement update": {},
    "ml account modelmanagement delete": {},
    "ml account modelmanagement set": {}
}

load_commands(ALL_COMMANDS)

for command in ALL_COMMANDS:
    register_command_arguments(command)
