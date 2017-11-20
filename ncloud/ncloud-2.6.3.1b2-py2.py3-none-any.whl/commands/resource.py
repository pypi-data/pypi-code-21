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
Subcommands for listing hardware resources assigned to you in the cloud.
"""
from functools import partial

from ncloud.commands.command import Command, build_subparser
from ncloud.config import RESOURCES
from ncloud.commands.command import LS


class List(Command):
    """
    List all resources assigned to your tenant.
    """
    @classmethod
    def parser(cls, subparser):
        list_res = subparser.add_parser(
            LS.name, aliases=LS.aliases,
            help=List.__doc__, description=List.__doc__
        )
        list_res.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config):
        return List.api_call(config, RESOURCES, return_json=True)


parser = partial(
    build_subparser, 'resource', ['res', 'r'], __doc__, (List,)
)
