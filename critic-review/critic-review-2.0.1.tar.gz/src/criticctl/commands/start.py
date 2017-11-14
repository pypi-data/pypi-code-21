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

import base

name = "start"
description = "Critic administration interface: Start Critic system"

def setup(parser):
    parser.add_argument(
        "--startup-timeout", type=int, default=30,
        help="Amount of time to wait for successful startup confirmation.")

    parser.set_defaults(run_as_root=True)

def main(arguments):
    subprocess.check_call(
        [sys.executable, "-m", "background.servicemanager", "--master",
         "--startup-timeout=%d" % arguments.startup_timeout])
