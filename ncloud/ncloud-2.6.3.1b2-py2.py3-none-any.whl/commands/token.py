#!/usr/bin/env python
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
Subcommands for managing tokens.
"""
from functools import partial
from ncloud.commands.command import (Command, build_subparser, REVOKE)
from ncloud.config import TOKENS


class Revoke(Command):
    """
    Revoke tokens
    """
    @classmethod
    def parser(cls, subparser):
        revoke = subparser.add_parser(REVOKE.name,
                                      aliases=REVOKE.aliases,
                                      help=Revoke.__doc__,
                                      description=Revoke.__doc__)
        revoke.add_argument("-t", "--tenant-ids",
                            nargs="+",
                            type=int,
                            help="Revoke all active tokens" +
                                 " in the specified list of tenant IDs.")
        revoke.add_argument("-a", "--alltokens",
                            action="store_true",
                            help="If true, revokes all active tokens.")
        revoke.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_ids, alltokens=False):
        data = {}
        data["tenant_ids"] = tenant_ids
        if alltokens:
            data["all_active_tokens"] = True

        return Revoke.api_call(config,
                               endpoint=TOKENS,
                               method="DELETE",
                               data=data,
                               return_json=True)


parser = partial(build_subparser, 'token', ['tkn'], __doc__, (Revoke,))
