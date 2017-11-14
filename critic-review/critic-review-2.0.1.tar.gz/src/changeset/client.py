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

import json
import socket
import errno

import base
import background

from textutils import indent

class ChangesetBackgroundServiceError(base.ImplementationError):
    def __init__(self, message):
        super(ChangesetBackgroundServiceError, self).__init__(
            "Changeset background service failed: %s" % message)

def requestChangesets(requests, async=False):
    response = background.utils.issue_command(
        "changeset", {"requests": requests, "async": async})

    if async:
        return

    if response["status"] == "error":
        raise ChangesetBackgroundServiceError(response["error"])

    errors = []

    for result in response["results"]:
        if "failure" in result:
            errors.append(result["failure"])

    if errors:
        raise ChangesetBackgroundServiceError(
            "one or more requests failed:\n%s" % "\n".join(map(indent, errors)))
