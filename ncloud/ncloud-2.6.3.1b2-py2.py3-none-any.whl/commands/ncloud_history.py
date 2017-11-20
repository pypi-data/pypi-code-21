# ----------------------------------------------------------------------------
# Copyright 2015-2017 Nervana Systems Inc.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ----------------------------------------------------------------------------
#
# # -*- coding: utf-8 -*-
"""
Subcommands for viewing all commands a user has made
"""
import logging

from ncloud.commands.command import Choices, Command, iso_8601_argument
from ncloud.commands.command import HIST
from ncloud.formatting.output import print_table
from ncloud.config import NCLOUD_CMD_HISTORY

logger = logging.getLogger()


class History(Command):
    """
    Lists ncloud commands used. Return every command used, command by command
    type, specific actions within command type (ex: model train), if commands
    were successful or not, commands based on start time, or
    arbitrary commands based on wildcard search.
    """

    @classmethod
    def parser(cls, subparser, command_types):
        fetch_command = subparser.add_parser(
            HIST.name, aliases=HIST.aliases, help=History.__doc__,
            description=History.__doc__)
        fetch_command.add_argument(
            "command_type", type=str, choices=Choices(command_types),
            nargs="?", help="Command type to further filter by. "
            "Without this, query on all command types.")
        fetch_command.add_argument(
            "action", type=str, nargs="?",
            help="Action to get history for. Usually the third argument in an "
                 "ncloud command. Examples include train, show, list. "
                 "Command type is required if action provided.")
        fetch_command.add_argument(
            "-n", "--count", type=int, default='10',
            help="Show up to n most recent commands. "
                 "For unlimited set n=0.")
        fetch_command.add_argument(
            "-s", "--was_successful", type=str,
            choices=('yes', 'no'),
            help="If set, returns only those commands that were or were not "
                 "successful")
        fetch_command.add_argument(
            "-b", "--before", type=iso_8601_argument,
            help="Filter on commands before this time. Format: YYYY-MM-DD. "
                 "Can be used in conjunction with the -a flag.")
        fetch_command.add_argument(
            "-a", "--after", type=iso_8601_argument,
            help="Filter on commands after this time. Format: YYYY-MM-DD. "
                 "Can be used in conjunction with the -b flag.")
        fetch_command.add_argument(
            "-w", '--wildcards', nargs='*',
            help="Wildcard phrases to return all ncloud commands that "
                 "contain any of those phrases. Ex: ncloud h -w model "
                 "custom-code-commit '-e 1' would return all ncloud "
                 "commands made with either the word model, custom code, "
                 "or 1 epoch.")
        fetch_command.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, command_type=None, action=None, count=10,
             was_successful=None, before=None, after=None, wildcards=None):
        """without command_type, return all command history list
           action will either be for a model (m) command type
           or an interact (i) command type
        """
        vals = {"count": count, "command_type": command_type,
                "action": action}
        # |= doesn't work for str and bool together :/
        was_successful = (was_successful == 'yes') if was_successful else None

        # add any other args that are set
        vals.update(
            {k: v for k, v in (
                ('was_successful', was_successful),
                ('before', before),
                ('after', after),
                ('wildcards', wildcards))
                if v is not None}
            )

        return History.api_call(
            config, NCLOUD_CMD_HISTORY, method="GET", params=vals,
            return_json=True)

    @staticmethod
    def display_after(config, args, res):
        print_table(res.get('commands', res))
