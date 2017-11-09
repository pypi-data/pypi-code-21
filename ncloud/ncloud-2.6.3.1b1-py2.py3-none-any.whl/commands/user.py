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
Subcommands for adding/deleting/modifying and listing users - admin privileges
required.
"""
from functools import partial

from ncloud.commands.command import (BaseList, NoRespCommand,
                                     build_subparser)
from ncloud.commands.command import (ADD, MODIFY, RM, SHOW, ADDGRP, RMGRP,
                                     PWRST)
from ncloud.formatting.output import print_table
from ncloud.config import USERS


class Add(NoRespCommand):
    """
    Add a new user to a tenant.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(ADD.name, aliases=ADD.aliases,
                                      help=Add.__doc__,
                                      description=Add.__doc__)
        parser.add_argument("email",
                            type=str,
                            help="new user's email address")
        parser.add_argument("first",
                            type=str,
                            help="new user's first name")
        parser.add_argument("last",
                            type=str,
                            help="new user's last name")
        parser.add_argument("groups",
                            nargs="+",
                            type=str,
                            help="list of group ID's user belongs to")
        parser.add_argument("-t", "--tenant-id",
                            type=int,
                            help="tenant_id for new user, " +
                            "if different than admin's")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, email, first, last, groups, tenant_id=None):
        data = {}
        data["first_name"] = first
        data["last_name"] = last
        data["email"] = email
        if len(groups) > 0:
            data["groups"] = groups
        if tenant_id is not None:
            data["user_tenantid"] = tenant_id

        endpoint = USERS
        method = "POST"
        return Add.api_call(config, endpoint=endpoint,
                            method=method, data=data, return_json=True)


class Modify(NoRespCommand):
    """
    Update the attributes of an individual user.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(MODIFY.name, aliases=MODIFY.aliases,
                                      help=Modify.__doc__,
                                      description=Modify.__doc__)
        parser.add_argument("user_id",
                            type=int,
                            help="ID of user to update")
        parser.add_argument("-f", "--first",
                            type=str,
                            help="new first name")
        parser.add_argument("-l", "--last",
                            type=str,
                            help="new last name")
        parser.add_argument("-p", "--password",
                            type=str,
                            help="New Password")
        parser.add_argument("-e", "--enabled",
                            type=int,
                            help="0 = disabled, 1 = enabled")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, user_id, first=None, last=None,
             password=None, enabled=None):
        data = {}
        data["operation"] = "replace"
        if first is not None:
            data["first_name"] = first
        if last is not None:
            data["last_name"] = last
        if password is not None:
            data["password"] = password
        if enabled is not None:
            data["enabled"] = enabled

        endpoint = USERS + str(user_id)
        method = "PATCH"
        return Modify.api_call(config, endpoint=endpoint,
                               method=method, data=data, return_json=True)


class Remove(NoRespCommand):
    """
    Delete a user.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(RM.name, aliases=RM.aliases,
                                      help=Remove.__doc__,
                                      description=Remove.__doc__)
        parser.add_argument("user_id",
                            type=int,
                            help="ID of the user to be deleted.")

        parser.add_argument("-t", "--tenant-id",
                            type=int,
                            help="tenant_id of user to delete, " +
                            "if different than admin's")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, user_id, tenant_id=None):
        endpoint = USERS + str(user_id)
        method = "DELETE"
        data = {}
        if tenant_id is not None:
            data["user_tenantid"] = tenant_id

        return Remove.api_call(config, endpoint=endpoint, data=data,
                               method=method, return_json=True)


class List(BaseList):
    """
    List users.
    """
    @classmethod
    def parser(cls, subparser):
        parser = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)

        parser.add_argument("-t", "--tenant-id",
                            type=int,
                            help="tenant_id to list users for")
        parser.add_argument("-a", "--listall",
                            action="store_true",
                            help="list users across all tenants")
        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, tenant_id=None, listall=False):
        vals = List.BASE_ARGS
        endpoint = USERS
        method = "GET"
        data = {}
        if tenant_id is not None:
            data["user_tenantid"] = tenant_id
        if listall:
            data["listall"] = True

        return List.api_call(config, endpoint=endpoint, data=data,
                             method=method, params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res:
            print_table(res['users'])


class Show(NoRespCommand):
    """
    Display details of an individual user.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(SHOW.name, aliases=SHOW.aliases,
                                      help=Show.__doc__,
                                      description=Show.__doc__)

        parser.add_argument("user_id",
                            type=int,
                            help="ID of user to show details of.")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, user_id):
        endpoint = USERS + str(user_id)
        method = "GET"
        return Show.api_call(config, endpoint=endpoint,
                             method=method, return_json=True)


class AddToGroup(NoRespCommand):
    """
    Add a user to specified groups.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(ADDGRP.name, aliases=ADDGRP.aliases,
                                      help=AddToGroup.__doc__,
                                      description=AddToGroup.__doc__)

        parser.add_argument("user_id",
                            type=int,
                            help="user_id of user to be added")

        parser.add_argument("group_ids",
                            type=int,
                            nargs="+",
                            help="group_ids of groups" +
                            " to which user will be added")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, user_id, group_ids):
        data = {}

        endpoint = USERS + str(user_id)
        method = "PATCH"
        data["operation"] = "add"
        data["group_ids"] = group_ids

        return AddToGroup.api_call(
            config, endpoint=endpoint, method=method, data=data,
            return_json=True)


class RemoveFromGroup(NoRespCommand):
    """
    Remove a user from groups.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(RMGRP.name, aliases=RMGRP.aliases,
                                      help=RemoveFromGroup.__doc__,
                                      description=RemoveFromGroup.__doc__)

        parser.add_argument("user_id",
                            type=int,
                            help="ID of user to remove from groups")

        parser.add_argument("group_ids",
                            type=int,
                            nargs="+",
                            help="group_ids of groups" +
                            " from which user will be removed")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, user_id, group_ids):
        data = {}
        endpoint = USERS + str(user_id)
        method = "PATCH"
        data["operation"] = "remove"
        data["group_ids"] = group_ids

        return RemoveFromGroup.api_call(
            config, endpoint=endpoint, method=method, data=data,
            return_json=True)


class ResetPassword(NoRespCommand):
    """
    Reset the password of the specified user.
    """
    @classmethod
    def parser(cls, subparser):
        parser = subparser.add_parser(PWRST.name, aliases=PWRST.aliases,
                                      help=ResetPassword.__doc__,
                                      description=ResetPassword.__doc__)

        parser.add_argument("email",
                            type=str,
                            help="email of the user to reset password.")

        parser.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, email):
        data = {}

        endpoint = USERS + "reset_authz_password"
        method = "POST"
        data["email"] = email

        return ResetPassword.api_call(
            config, endpoint=endpoint, token_needed=False, method=method,
            data=data, return_json=True)


parser = partial(
    build_subparser, 'user', ['u'], __doc__,
    (Add, Modify, Remove, List, Show, AddToGroup, RemoveFromGroup,
     ResetPassword)
)
