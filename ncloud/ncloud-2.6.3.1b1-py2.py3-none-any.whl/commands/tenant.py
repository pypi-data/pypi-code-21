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
Subcommands for adding/deleting/modifying and listing tenants - admin
privileges required.
"""
from functools import partial

from ncloud.commands.command import Command, NoRespCommand, build_subparser
from ncloud.commands.command import ADD, MODIFY, LS, RM, SHOW
from ncloud.formatting.output import print_table
from ncloud.config import TENANTS


class Add(NoRespCommand):
    """
    Add a new tenant to the cloud.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(ADD.name, aliases=ADD.aliases,
                                      help=Add.__doc__,
                                      description=Add.__doc__)
        parser.add_argument("name",
                            type=str,
                            help="new tenant's name")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, name):
        data = {}
        data["name"] = name
        endpoint = TENANTS
        method = "POST"
        return Add.api_call(config, endpoint=endpoint,
                            method=method, data=data, return_json=True)


class Modify(NoRespCommand):
    """
    Update the attributes of an individual tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(MODIFY.name, aliases=MODIFY.aliases,
                                      help=Modify.__doc__,
                                      description=Modify.__doc__)
        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to be modified")
        parser.add_argument("name",
                            type=str,
                            help="tenant's new name")
        parser.add_argument("-e", "--enabled",
                            type=int,
                            help="0 = disabled, 1 = enabled")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id, name=None, enabled=None):
        data = {}
        data["operation"] = "replace"
        if name is not None:
            data["name"] = name
        if enabled is not None:
            data["enabled"] = enabled

        endpoint = TENANTS + str(tenant_id)
        method = "PATCH"
        return Modify.api_call(config, endpoint=endpoint,
                               method=method, data=data, return_json=True)


class Remove(Command):
    """
    Delete a tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(RM.name, aliases=RM.aliases,
                                      help=Remove.__doc__,
                                      description=Remove.__doc__)

        parser.add_argument("tenant_id",
                            type=int,
                            help="ID of tenant to be deleted")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id):
        endpoint = TENANTS + str(tenant_id)
        method = "DELETE"
        return Remove.api_call(
            config, endpoint=endpoint, method=method, return_json=True)


class TenantDisplay(Command):
    """Base class for Show and List classes"""
    @classmethod
    def parser(cls, subparser, klass, tenant_id=None):
        parser = subparser.add_parser(klass.name, aliases=klass.aliases,
                                      help=klass.__doc__,
                                      description=klass.__doc__)
        if tenant_id:
            parser.add_argument("tenant_id", type=int,
                                help="ID of tenant to show details of.")
        parser.add_argument("--details", action="store_true",
                            help="Show more details about " + "the tenant."
                            if tenant_id else "tenants.")
        parser.add_argument('-u', "--user-details", action="store_true",
                            help="Return user details rather than just the "
                            "count of all of them. NOTE: formatting will be a "
                            "bit messed up if flag passed.")
        parser.add_argument('-g', "--group-details", action="store_true",
                            help="Return group details rather than just "
                            "their names. NOTE: formatting will be a bit "
                            "messed up if flag passed.")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, endpoint, details, user_details, group_details):
        data = {
            'endpoint': endpoint,
            'method': 'GET',
            'params': {'details': details, 'user_details': user_details,
                       'group_details': group_details},
            'return_json': True
        }
        return TenantDisplay.api_call(config, **data)

    @staticmethod
    def display_after(res, data_location):
        if res:
            print_table(res[data_location])


class List(TenantDisplay):
    """
    List tenants.
    """
    @classmethod
    def parser(cls, subparser):
        super(List, cls).parser(subparser, LS)

    @staticmethod
    def call(config, details=False, user_details=False, group_details=False):
        return TenantDisplay.call(
            config, TENANTS, details, user_details, group_details)

    @staticmethod
    def display_after(config, args, res):
        return TenantDisplay.display_after(res, 'tenants')


class Show(TenantDisplay):
    """
    Display details of an individual tenant.
    """
    @classmethod
    def parser(cls, subparser):
        super(Show, cls).parser(subparser, SHOW, tenant_id=True)

    @staticmethod
    def call(config, tenant_id, details=False, user_details=False,
             group_details=False):
        return TenantDisplay.call(config, TENANTS + str(tenant_id), details,
                                  user_details, group_details)

    @staticmethod
    def display_after(config, args, res):
        return TenantDisplay.display_after(res, 'tenant')


parser = partial(
    build_subparser, 'tenant', ['t'], __doc__,
    (Add, Modify, Remove, List, Show)
)
