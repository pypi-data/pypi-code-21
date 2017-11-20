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
Subcommands for viewing and managing machines.
"""
from functools import partial
import os

from ncloud.commands.command import Command, build_subparser
from ncloud.config import MACHINES
from ncloud.commands.command import LS, SHOW, MODIFY
from ncloud.formatting.output import print_table


class List(Command):
    """
    List all machines.
    """
    @classmethod
    def parser(cls, subparser):
        list_machines = subparser.add_parser(
            LS.name, aliases=LS.aliases,
            help=List.__doc__, description=List.__doc__
        )
        list_machines.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return List.api_call(config, MACHINES, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['machines'])


class Show(Command):
    """
    Show machine.
    """
    @classmethod
    def parser(cls, subparser):
        show_machine = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                            help=Show.__doc__,
                                            description=Show.__doc__)
        show_machine.set_defaults(func=cls.arg_call)

        show_machine.add_argument("machine_id",
                                  type=int,
                                  help="machine_id to show details of")

    @staticmethod
    def call(config, machine_id):
        return Show.api_call(
            config, os.path.join(MACHINES, str(machine_id)), return_json=True)


class Modify(Command):
    """
    Update the attributes of an individual machine.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(MODIFY.name, aliases=MODIFY.aliases,
                                      help=Modify.__doc__,
                                      description=Modify.__doc__)
        parser.add_argument("machine_id",
                            type=int,
                            help="ID of machine to update")
        parser.add_argument("-o", "--operation",
                            type=str,
                            help="add, replace, or remove")
        parser.add_argument("-t", "--tenant_id",
                            type=int,
                            help="new tenant assignment")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, machine_id, operation, tenant_id=None):
        data = {"operation": operation}
        if tenant_id is not None:
            data["tenant_id"] = tenant_id

        endpoint = os.path.join(MACHINES, str(machine_id))
        return Modify.api_call(config, endpoint=endpoint,
                               method="PATCH", data=data, return_json=True)


parser = partial(
    build_subparser, 'machine', ['mach'], __doc__, (List, Show, Modify)
)
