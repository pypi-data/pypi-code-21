# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
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

import os
import signal

from operation import (Operation, OperationResult, Optional, OperationError,
                       OperationFailure)

import api
import background

class RestartService(Operation):
    def __init__(self):
        Operation.__init__(self, { "service_name": str })

    def process(self, db, user, service_name):
        Operation.requireRole(db, "administrator", user)

        response = background.utils.issue_command(
            "servicemanager",
            {"command": "restart", "service": service_name, "timeout": 10})

        if response["status"] == "error":
            raise OperationFailure(
                "restartfailed",
                title="Failed to restart service",
                message=response["error"])

        return OperationResult()

class GetServiceLog(Operation):
    def __init__(self):
        Operation.__init__(self, { "service_name": str, "lines": Optional(int) })

    def process(self, db, user, service_name, lines=40):
        if service_name not in api.critic.settings().services:
            raise OperationError("unknown service: %s" % service_name)

        logs_dir = api.critic.settings().paths.logs
        logfile_path = os.path.join(logs_dir, f"{service_name}.log")

        try:
            with open(logfile_path, "r", encoding="utf-8") as logfile:
                return OperationResult(
                    lines=logfile.read().splitlines()[-lines:])
        except OSError as error:
            raise OperationError("failed to open logfile: %s" % error)

