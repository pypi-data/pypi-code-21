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

import distutils.spawn
import logging
import os
import subprocess
import sys

logger = logging.getLogger(__name__)

import api

TEMPLATE = """

[Unit]
Description=Critic code review system
Requires=postgresql.service
After=postgresql.service

[Service]
Type=forking
PIDFile=%(pidfile_path)s
ExecStart=%(criticctl_path)s start
KillMode=mixed
TimeoutStartSec=60

[Install]
WantedBy=multi-user.target

"""

name = "install:systemd-service"
description = "Install a systemd service for the Critic system."

def setup(critic, parser):
    parser.add_argument(
        "--service-file", default="/etc/systemd/system/critic.service",
        help="Service file to create.")
    parser.add_argument(
        "--force", action="store_true",
        help="Overwrite an existing service file instead of aborting.")
    parser.add_argument(
        "--start-service", action="store_true",
        help="Start the service after creating the service file.")

    parser.set_defaults(need_session=True, run_as_root=True)

def main(critic, arguments):
    from . import fail

    systemctl = distutils.spawn.find_executable("systemctl")
    if not systemctl:
        fail("Could not find `systemctl` executable in $PATH!")

    if os.path.exists(arguments.service_file):
        if arguments.force:
            logger.debug("%s: file already exists; will overwrite",
                         arguments.service_file)
        else:
            fail("%s: file already exists!" % arguments.service_file)

    service_name = os.path.basename(arguments.service_file)

    parameters = {
        "pidfile_path": os.path.join(
            api.critic.settings().paths.runtime, "servicemanager.pid"),
        "criticctl_path": sys.argv[0],
    }

    with open(arguments.service_file, "w", encoding="utf-8") as file:
        print((TEMPLATE % parameters).strip(), file=file)

    logger.info("Created systemd service file: %s", arguments.service_file)

    subprocess.check_output([systemctl, "daemon-reload"])

    logger.info("Reloaded systemd daemon")

    if arguments.start_service:
        subprocess.check_call([systemctl, "start", service_name])

        logger.info("Started service: %s", service_name)
