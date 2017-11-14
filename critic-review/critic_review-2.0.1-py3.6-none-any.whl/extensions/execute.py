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

import errno
import os
import socket
import subprocess
import time
import json

import api
import auth
import base
import background
import background.changeset
import background.branchtracker
import background.maildelivery
import dbutils
import gitutils

from extensions.extension import Extension

def get_process_params(settings, flavor):
    executable = settings.extensions.flavors[flavor]["executable"]
    library = os.path.join(
        settings.paths.home, "library",
        settings.extensions.flavors[flavor]["library"])

    return {
        "argv": [executable, "critic-launcher.js"],
        "cwd": library,
    }

class ProcessException(Exception):
    pass

class ProcessError(ProcessException):
    def __init__(self, message):
        super(ProcessError, self).__init__(
            "Failed to execute process: %s" % message)

class ProcessTimeout(ProcessException):
    def __init__(self, timeout):
        super(ProcessTimeout, self).__init__(
            "Process timed out after %d seconds" % timeout)

class ProcessFailure(ProcessException):
    def __init__(self, returncode, stderr):
        super(ProcessFailure, self).__init__(
            "Process returned non-zero exit status %d" % returncode)
        self.returncode = returncode
        self.stderr = stderr

def executeProcess(db, manifest, role_name, script, function, extension_id,
                   user_id, argv, timeout, stdin=None, rlimit_rss=256):
    # If |user_id| is not the same as |db.user|, then one user's access of the
    # system is triggering an extension on behalf of another user.  This will
    # for instance happen when one user is adding changes to a review,
    # triggering an extension filter hook set up by another user.
    #
    # In this case, we need to check that the other user can access the
    # extension.
    #
    # If |user_id| is the same as |db.user|, we need to use |db.profiles|, which
    # may contain a profile associated with an access token that was used to
    # authenticate the user.
    if user_id != db.user.id:
        user = dbutils.User.fromId(db, user_id)
        authentication_labels = auth.Database.get().getAuthenticationLabels(
            user)
        profiles = [auth.AccessControlProfile.forUser(
            db, user, authentication_labels)]
    else:
        authentication_labels = db.authentication_labels
        profiles = db.profiles

    extension = Extension.fromId(db, extension_id)
    if not auth.AccessControlProfile.isAllowedExtension(
            profiles, "execute", extension):
        raise auth.AccessDenied("Access denied to extension: execute %s"
                                % extension.getKey())

    flavors = api.critic.settings().extensions.flavors
    flavor = manifest.flavor

    if manifest.flavor not in flavors:
        flavor = api.critic.settings().extensions.default_flavor

    stdin_data = "%s\n" % json.dumps({
        "library_path": flavors[flavor]["library"],
        "rlimit": { "rss": rlimit_rss },
        "hostname": api.critic.settings().system.hostname,
        "dbparams": base.configuration()["database.parameters"],
        "git": gitutils.git(),
        "python": api.critic.settings().executables.python,
        "python_path": api.critic.settings().paths.settings,
        "repository_work_copy_path": api.critic.settings().extensions.workcopy_dir,
        "changeset_address": background.changeset.ChangesetService.socket_path(),
        "branchtracker_pid_path": background.branchtracker.BranchTrackerService.pidfile_path(),
        "maildelivery_pid_path": background.maildelivery.MailDeliveryService.pidfile_path(),
        "is_development": api.critic.settings().system.is_development,
        "extension_path": manifest.path,
        "extension_id": extension_id,
        "user_id": user_id,
        "authentication_labels": list(authentication_labels),
        "role": role_name,
        "script_path": script,
        "fn": function,
        "argv": argv
    })

    if stdin is not None:
        stdin_data += stdin

    command = {
        "stdin_data": stdin_data,
        "flavor": flavor,
        "timeout": timeout,
    }

    # Double the timeout. Timeouts are primarily handled by the extension runner
    # service, which returns an error response on timeout. This timeout here is
    # thus mostly to catch the extension runner service itself timing out.
    command_timeout = timeout * 2

    try:
        response = background.utils.issue_command(
            "extensionrunner", command, command_timeout)
    except background.utils.TimeoutError:
        raise ProcessTimeout(command_timeout)

    if response["status"] == "timeout":
        raise ProcessTimeout(timeout)

    if response["status"] == "error":
        raise ProcessError(response["error"])

    if response["returncode"] != 0:
        raise ProcessFailure(response["returncode"], response["stderr"])

    return response["stdout"].encode("latin-1")
