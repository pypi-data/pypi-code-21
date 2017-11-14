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

import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

import api
import base

from .. import tasks

name = "run-task"
description = "Critic administration interface: Run task"
allow_missing_configuration = True

def setup(parser):
    parser.set_defaults(parser=parser)

    subparsers = parser.add_subparsers(help="Task to run.")

    try:
        configuration = base.configuration()
    except base.MissingConfiguration:
        configuration_missing = True
        critic = None
    else:
        configuration_missing = False
        with tasks.as_user(name=configuration["system.username"]):
            critic = api.critic.startSession(for_system=True)

    for task_module in tasks.modules:
        if configuration_missing:
            if not getattr(task_module, "allow_missing_configuration", False):
                continue

        task_parser = subparsers.add_parser(
            task_module.name,
            description=task_module.description)
        task_parser.set_defaults(task_main=task_module.main)
        task_module.setup(critic, task_parser)

    if critic:
        with critic:
            pass

def main(*args):
    arguments = args[-1]

    if not hasattr(arguments, "task_main"):
        arguments.parser.print_help()
        return 0

    try:
        arguments.task_main(*args)
    except tasks.TaskFailed:
        return 1
