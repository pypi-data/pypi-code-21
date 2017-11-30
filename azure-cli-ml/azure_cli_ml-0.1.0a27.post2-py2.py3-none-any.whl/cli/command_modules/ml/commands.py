# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

#pylint: disable=line-too-long

import json
from ._constants import MLC_MODELS_PATH
from ._constants import MLC_CLIENT_PATH
from importlib import import_module
from azure.cli.core.util import CLIError
from azure.cli.command_modules.ml.commands_utility import load_commands
from azure.cli.command_modules.ml.all_parameters import register_command_arguments
from pkg_resources import working_set
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
from ._ml_cli_error import MlCliError

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
    try:
        ml_cli_version = working_set.by_key['azure-cli-ml'].version
        if isinstance(exc, MlCliError):
            response = exc.to_json()
            response['Azure-cli-ml Version'] = ml_cli_version
            raise CLIError(json.dumps(response, indent=4, sort_keys=True))
        elif isinstance(exc, CLIError):
            response = {'Error': exc.args[0]}
            response['Azure-cli-ml Version'] = ml_cli_version
            raise CLIError(json.dumps(response, indent=4, sort_keys=True))
        elif isinstance(exc, ErrorResponseWrapperException):
            # Thrown by MLC
            exc_to_process = exc.error.error
            if exc_to_process:
                response = {'Azure-cli-ml Version': ml_cli_version}
                if exc_to_process.code:
                    response['Response Code'] = exc_to_process.code
                if exc_to_process.message:
                    response['Response Content'] = exc_to_process.message
                if exc_to_process.details:
                    response['Response Details'] = exc_to_process.details
                raise CLIError(json.dumps(response, indent=4, sort_keys=True))
    except CLIError:
        raise
    except:
        pass

    response = {'Azure-cli-ml Version': ml_cli_version,
                'Error': exc}
    raise CLIError(response)


ALL_COMMANDS = {
    # "ml service create batch": {"formatter_class": AmlHelpFormatter},
    # "ml service run batch": {"formatter_class": AmlHelpFormatter},
    # "ml service list batch": {},
    # "ml service show batch": {},
    # "ml service delete batch": {},
    # "ml service showjob batch": {},
    # "ml service listjobs batch": {},
    # "ml service canceljob batch": {},

    "ml env local": {"exception_handler": _handle_exceptions},
    "ml env cluster": {"exception_handler": _handle_exceptions},
    "ml env show": {"exception_handler": _handle_exceptions, "transform": transform_mlc_resource},
    "ml env setup": {"exception_handler": _handle_exceptions},
    "ml env list": {"exception_handler": _handle_exceptions, "transform": transform_mlc_resource_list},
    "ml env delete": {'exception_handler': _handle_exceptions},
    "ml env set": {'exception_handler': _handle_exceptions},
    "ml env get-credentials": {"exception_handler": _handle_exceptions},

    "ml service create realtime": {"exception_handler": _handle_exceptions},
    "ml service list realtime": {"exception_handler": _handle_exceptions, "transform": transform_service_list, "table_transformer": table_transform_service_list},
    "ml service show realtime": {"exception_handler": _handle_exceptions, "transform": transform_service_show, "table_transformer": table_transform_service_show},
    "ml service delete realtime": {"exception_handler": _handle_exceptions},
    "ml service run realtime": {"exception_handler": _handle_exceptions},
    "ml service update realtime": {"exception_handler": _handle_exceptions},
    'ml service keys realtime': {"exception_handler": _handle_exceptions},
    'ml service usage realtime': {"exception_handler": _handle_exceptions},
    'ml service logs realtime': {"exception_handler": _handle_exceptions},

    "ml model register": {"exception_handler": _handle_exceptions},
    "ml model show": {"exception_handler": _handle_exceptions, "transform": transform_model_show, "table_transformer": table_transform_model_show},
    "ml model list": {"exception_handler": _handle_exceptions, "transform": transform_model_list, "table_transformer": table_transform_model_list},

    "ml manifest create": {"exception_handler": _handle_exceptions},
    "ml manifest show": {"exception_handler": _handle_exceptions, "transform": transform_manifest_show, "table_transformer": table_transform_manifest_show},
    "ml manifest list": {"exception_handler": _handle_exceptions, "transform": transform_manifest_list, "table_transformer": table_transform_manifest_list},

    "ml image create": {"exception_handler": _handle_exceptions},
    "ml image show": {"exception_handler": _handle_exceptions, "transform": transform_image_show, "table_transformer": table_transform_image_show},
    "ml image list": {"exception_handler": _handle_exceptions, "transform": transform_image_list, "table_transformer": table_transform_image_list},
    "ml image usage": {"exception_handler": _handle_exceptions},

    "ml account modelmanagement create": {"exception_handler": _handle_exceptions},
    "ml account modelmanagement show": {"exception_handler": _handle_exceptions, "transform": transform_mma_show, "table_transformer": table_transform_mma_show},
    "ml account modelmanagement list": {"exception_handler": _handle_exceptions, "transform": transform_mma_list, "table_transformer": table_transform_mma_list},
    "ml account modelmanagement update": {"exception_handler": _handle_exceptions},
    "ml account modelmanagement delete": {"exception_handler": _handle_exceptions},
    "ml account modelmanagement set": {"exception_handler": _handle_exceptions}
}

load_commands(ALL_COMMANDS)

for command in ALL_COMMANDS:
    register_command_arguments(command)
