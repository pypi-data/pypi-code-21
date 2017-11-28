# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

""" commands_utility.py, A file for simplifying how commands are registered with the cli."""

# pylint: disable=line-too-long
from azure.cli.core.commands import cli_command
import os
import json
from ._ml_cli_error import MlCliError

# mgmt_path = 'azure.mgmt.machinelearningcompute.operations.operationalization_clusters_operations#OperationalizationClustersOperations.'

fmt_dict = {
    'mgmt_path': 'azure.cli.command_modules.ml._mlc.operations.operationalization_clusters_operations#OperationalizationClustersOperations.'
}


def load_commands(commands):
    details = introspect()
    for key, value in commands.items():
        command_details = details[key]
        cli_command(__name__, command_details["cli_command"],
                    command_details["command_function"].format(**fmt_dict),
                    **(commands[key]))


def introspect():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'command_details.json')) as data_file:
            return json.load(data_file)
    except IOError as error:
        raise MlCliError('Error loading commands from json: {}'.format(error))
