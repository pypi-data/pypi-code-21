# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

# pylint: disable=line-too-long

import argparse
from azure.cli.core.commands import register_cli_argument, register_extra_cli_argument, _cli_extra_argument_registry
from azure.cli.core.commands.parameters import ignore_type
from azure.cli.command_modules.ml.commands_utility import introspect
from ._mma.models.mma_enums import SkuName
from ._constants import SUPPORTED_RUNTIMES


def register_command_arguments(command_name):
    """ Takes the name of a command (ex: "ml execute start") and cycles through all
        arguments for it, registering all of them.
    """

    details = introspect()
    command = details[command_name].copy()
    for key in command["arguments"].keys():
        try:
            arguments = command["arguments"][key]

            if "positional_argument" in command["arguments"][key]:
                positional_argument(command, key, arguments)
            else:
                args = get_arguments(arguments, key)
                register_cli_argument(command["cli_command"], key, **args)
        except KeyError as error:
            print(error)
            print("The given command is not part of command_details.json: ", key)


def get_arguments(arguments, key):
    """ Takes the dictionary of arguments and modifies it based on args that need
        additional modification. Uses key to check if description needs to be replaced.
    """

    if "long_form" in arguments and "short_form" in arguments:
        arguments["options_list"] = get_options(arguments)
    arguments.pop('long_form', None)
    arguments.pop('short_form', None)

    if "description" in arguments:
        arguments["help"] = process_description(arguments["description"], key)
    arguments.pop('description', None)

    if "default" in arguments:
        arguments["default"] = process_default(arguments["default"])

    if "arg_type" in arguments:
        arguments["arg_type"] = process_arg_type(arguments["arg_type"])

    if "type" in arguments:
        arguments["type"] = process_type(arguments["type"])
    return arguments


def get_options(arguments):
    """ Converts long_form/short_form into the appropriate tuple for argument
        registration.
    """

    if arguments["long_form"] != '' and arguments["short_form"] != '':
        return (arguments["long_form"], arguments["short_form"])
    if arguments["long_form"] == '':
        return (arguments["short_form"], )
    return (arguments["long_form"], )


def positional_argument(command, key, arg):
    """Ugly workaround for positional arguments"""

    # Positional argument workaround. Consumes every argument after the last
    # positional argument.
    register_extra_cli_argument(
        command["cli_command"],
        key,
        options_list=[key],
        help=arg["description"],
        nargs=argparse.REMAINDER)
    # AzureCLI helpfully adds leading dashes to the argument -- we don't want
    # that for positional arguments!
    _cli_extra_argument_registry[command["cli_command"]][key].options_list = [
        key]
    # Avoid specifying dest twice.
    _cli_extra_argument_registry[command["cli_command"]][key].type.settings.pop(
        'dest')


def process_default(value):
    if value == "None":
        return None
    return value


def process_types(value):
    if value == "int":
        return int
    if value == "[]":
        return []
    return value


def process_arg_type(value):
    if value == "ignore_type":
        return ignore_type
    return value


def process_type(value):
    if value == "int":
        return int
    return value


def process_description(value, key):
    if value == "argparse.SUPPRESS":
        return argparse.SUPPRESS
    if key == "target_runtime" or key == "runtime":
        return value + '{}'.format('|'.join(SUPPORTED_RUNTIMES.keys()))
    if key == "sku_name":
        return value + '{}'.format('|'.join([name.value for name in SkuName]))
    return value
