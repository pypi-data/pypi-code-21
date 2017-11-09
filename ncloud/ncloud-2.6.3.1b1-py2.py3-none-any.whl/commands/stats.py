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
Subcommands for listing analytics information.
"""
from functools import partial

from ncloud.commands.command import Command, build_subparser
from ncloud.commands.command import LS
from ncloud.formatting.output import print_table
from ncloud.util.arg_processor import process_args
from ncloud.config import STATS


class List(Command):
    @classmethod
    def parser(cls, subparser):
        stats = subparser.add_parser(LS.name, aliases=LS.aliases,
                                     help=List.__doc__,
                                     description=List.__doc__)
        stats.add_argument("-m", "--models", action="store_true",
                           help="Show models stats.")
        stats.add_argument("-t", "--time", default=0, type=int, help="Show "
                           "stats for models submitted in last n days. "
                           "Default unlimited.")
        stats_tenant_option = stats.add_mutually_exclusive_group()
        stats_tenant_option.add_argument(
            "-s", "--tenant-stats", action="store_true",
            help="Show all tenants' stats, must be admin.")
        stats_tenant_option.add_argument(
            "-i", "--tenant-id", type=int, help="Show a single tenant's "
            "stats, must be admin.")
        stats.add_argument(
            "-p", "--page", default=1, type=int, help="Page number.")
        stats.add_argument("-r", "--per-page", default=20, type=int,
                           help="Number of results per page.")
        stats.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, models=False, time=0, tenant_id=None, tenant_stats=False,
             page=1, per_page=20):
        vals = process_args(locals(), ignore_none=True)
        # if time or models not set, set models anyway
        if not (models or time):
            vals["models"] = True
            vals["time"] = 0
        return List.api_call(config, STATS, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res)

parser = partial(
    build_subparser, 'stats', ['sta'], __doc__, (List,)
)
