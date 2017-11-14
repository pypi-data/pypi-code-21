# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2017 the Critic contributors, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import json
import sys

import api

name = "settings"
description = "Access Critic's system settings."

def setup(parser):
    parser.add_argument(
        "--indent", type=int,
        help="Amount of indentation in JSON output.")
    parser.set_defaults(need_session=True, parser=parser)

    operations = parser.add_subparsers(help="Operation")

    list_parser = operations.add_parser(
        "list", help="List settings.")
    list_parser.set_defaults(operation="list")

    get_parser = operations.add_parser(
        "get", help="Retrieve one or more settings.")
    get_parser.set_defaults(operation="get")
    get_parser.add_argument(
        "key", nargs="+",
        help="Settings to retrieve.")

    get_all_parser = operations.add_parser(
        "get-all", help="Retrieve all settings.")
    get_all_parser.set_defaults(operation="get-all")

    set_parser = operations.add_parser(
        "set", help="Update a setting's value.")
    set_parser.set_defaults(operation="set")
    set_parser.add_argument(
        "key", help="Setting to update.")
    set_parser.add_argument(
        "value", nargs="?",
        help="New value. Read from stdin if omitted.")

def main(critic, arguments):
    if not hasattr(arguments, "operation"):
        arguments.parser.print_help()
        return 0

    try:
        if arguments.operation == "list":
            response = [
                setting.id
                for setting in api.systemsetting.fetchAll(critic)
            ]
        elif arguments.operation == "get":
            response = {}
            for key in arguments.key:
                response[key] = api.systemsetting.fetch(critic, key).value
        elif arguments.operation == "get-all":
            response = {
                setting.id: setting.value
                for setting in api.systemsetting.fetchAll(critic)
            }
        else:
            if arguments.value:
                value = json.loads(arguments.value)
            else:
                value = json.load(sys.stdin)
            setting = api.systemsetting.fetch(critic, arguments.key)
            with api.transaction.Transaction(critic) as transaction:
                transaction.setSystemSetting(setting, value)
            response = None
    except api.systemsetting.SystemSettingError as error:
        print(str(error), file=sys.stderr)
        return 1

    if response is not None:
        json.dump(response, sys.stdout, indent=arguments.indent)
        print()
