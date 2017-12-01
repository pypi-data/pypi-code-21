# -*- coding: utf-8 -*-
#
# Copyright (c) 2016-2017 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Subcommands for launching and managing interactive environments.
"""
import logging
from functools import partial
import os

from ncloud.commands.command import (BaseList, Command, Results,
                                     build_subparser, SHOW, START, STOP,
                                     ShowLogs)
from ncloud.completers import InteractiveSessionCompleter
from ncloud.config import INTERACT
from ncloud.formatting.output import print_table
from ncloud.util.arg_processor import process_args

logger = logging.getLogger()


class Show(ShowLogs):
    """
    Show interactive session details.
    """

    @classmethod
    def parser(cls, subparser):
        interact = super(Show, cls).parser(
            subparser, SHOW.aliases, Show.__doc__, Show.__doc__
        )

        interact.add_argument(
            "id", type=int,
            help="id of the interactive session to show details of."
        ).completer = InteractiveSessionCompleter

        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, id, log=False, log_follow=False):
        show_path = os.path.join(INTERACT, str(id), 'outputs')

        if not (log or log_follow):
            return Show.api_call(config, show_path, return_json=True)

        params = {'log_file': "launcher.log"}
        show_path = os.path.join(show_path, 'launcher.log')

        if log:
            params.update({'format': 'zip'})
            ShowLogs.read_log(config, show_path, params)

        elif log_follow:
            params.update({'tail': 'True', 'format': 'url'})
            ShowLogs.read_log_tail(config, show_path, params)

    @staticmethod
    def display_after(config, args, res):
        if res is not None and 'uuid' in res:
            res['url'] = config.get_host() \
                             .rstrip('/') + '/interact/' + res['uuid']
            del res['uuid']
        print_table(res)


class Start(Command):
    """
    Launch an interactive ipython notebook environment.
    """

    @classmethod
    def parser(cls, subparser):
        interact = subparser.add_parser(START.name, aliases=START.aliases,
                                        description=Start.__doc__,
                                        help=Start.__doc__)

        interact.add_argument("-v", "--volume_ids", nargs='+',
                              help="IDs of volumes to mount in notebook. "
                                   " Example: 2,3,4")
        interact.add_argument("-e", "--environment",
                              help="Name of the deep learning environment to "
                                   "use. The specified environment must be one"
                                   " listed in `ncloud environment ls -t "
                                   "interact`. If not supplied, default"
                                   "environment will be used.")
        interact.add_argument("-f", "--framework-version",
                              help="Neon tag, branch or commit to use.")
        interact.add_argument("-i", "--resume-model-id", type=int,
                              help="Start training a new model using the state"
                                   " parameters of a previous one.")
        interact.add_argument("-g", "--gpus", default=1, type=int,
                              help="Number of GPUs to train this model with.")
        interact.add_argument("-u", "--custom-code-url",
                              help="URL for codebase containing custom neon "
                                   "scripts and extensions.")
        interact.add_argument("-c", "--custom-code-commit", default="master",
                              help="Commit ID or branch specifier for custom "
                                   "code repo.")
        interact.add_argument("-n", "--name",
                              help="Name of this interactive ipython "
                                   "notebook. If not supplied, one will be "
                                   "provided for you.")
        interact.add_argument("-L", "--log_immediately", action="store_true",
                              help="Immediately start tail interact logs."
                                   "Equivalent to running `ncloud interact "
                                   "show -L`.")
        interact_auth = interact.add_mutually_exclusive_group()
        interact_auth.add_argument(
            "-p", "--password",
            help="Password to enter once notebook starts up. If no password "
                 "entered, need to nter token provided in the `ncloud i show "
                 "{id} -l` log at the end. Incompatible with unsecure flag."
        )
        interact_auth.add_argument(
            "--unsecure", action="store_true",
            help="Latest notebook strongly recommends authentication. If you "
                 "wish to bypass this, pass this flag and you won't have to "
                 "enter a token or password on notebook start. Incompatible "
                 "with password flag.")

        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, gpus=1, volume_ids=None, framework_version=None,
             custom_code_url=None, resume_model_id=None,
             custom_code_commit=None, name=None, password=None,
             unsecure=False, log_immediately=False, environment=None):
        api_args = process_args(locals(), ignore_none=True)
        return Start.api_call(
            config, INTERACT, method="POST", data=api_args, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res and 'uuid' in res:
            res['url'] = config.get_host() \
                             .rstrip('/') + '/interact/' + res['uuid']
            del res['uuid']
        print_table(res)

        if args.log_immediately:
            Show.call(config, res['id'], log_follow=True)


class Stop(Command):
    """
    Stop an interactive environment.
    """

    @classmethod
    def parser(cls, subparser):
        interact = subparser.add_parser(STOP.name, aliases=STOP.aliases,
                                        help=Stop.__doc__,
                                        description=Stop.__doc__)
        group = interact.add_mutually_exclusive_group(required=True)
        group.add_argument("session_ids", nargs="*", type=int, default=[],
                           help="id or list of IDs of sessions to stop")
        group.add_argument("-a", "--all_sessions", action="store_true",
                           help="Stop all running sessions the user has "
                                "access to")
        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, session_ids, all_sessions=False):
        return Stop.api_call(
            config, INTERACT, method="Delete", return_json=True,
            params={'instance_ids': session_ids}
        )


class List(BaseList):
    """
    List interactive sessions.
    """

    @classmethod
    def parser(cls, subparser):
        interact = super(List, cls).parser(
            subparser, List.__doc__, List.__doc__)
        interact.add_argument('-a', "--all", action="store_true",
                              help="Show sessions in all states.")
        interact.set_defaults(func=cls.arg_call)

    @staticmethod
    def call(config, all=False):
        vals = List.BASE_ARGS
        if not all:
            vals["filter"] = ["Ready", "Launching", "Scheduling"]

        return List.api_call(
            config, INTERACT, method="GET", params=vals, return_json=True)

    @staticmethod
    def display_after(config, args, res):
        if res and 'sessions' in res:
            # adjust content for display, show full URL rather than uuid
            res = res['sessions']
            for r in res:
                r['url'] = config.get_host().rstrip('/') + \
                           '/interact/' + r['uuid']
                del r['uuid']
        print_table(res)


InteractResults = Results(
    "interact",
    InteractiveSessionCompleter,
    INTERACT
)
parser = partial(
    build_subparser, 'interact', ['i'], __doc__, (
        Start, List, Stop, Show, InteractResults)
)
