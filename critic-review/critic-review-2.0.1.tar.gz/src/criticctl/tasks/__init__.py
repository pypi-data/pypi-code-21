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

import contextlib
import logging
import os
import pwd
import re
import subprocess
import sys

logger = logging.getLogger(__name__)

from . import install
from . import install_preferences
from . import install_systemd_service
from . import frontend_nginx
from . import frontend_uwsgi
from . import backend_uwsgi
from . import calibrate_pwhash

modules = [
    install,
    install_preferences,
    install_systemd_service,
    frontend_nginx,
    frontend_uwsgi,
    backend_uwsgi,
    calibrate_pwhash,
]

class TaskFailed(Exception):
    pass

def fail(message, *additional):
    import textutils

    def for_each_line(fn, string):
        for line in textutils.reflow(string, line_length=70).splitlines():
            fn(line)

    for_each_line(logger.error, f"{message}")

    for string in additional:
        for_each_line(logger.info, string)

    sys.exit(1)

@contextlib.contextmanager
def temporary_cwd(cwd, use_fallback=True):
    previous_cwd = os.getcwd()

    try:
        os.chdir(cwd)
    except OSError:
        if not use_fallback:
            raise
        os.chdir("/")

    try:
        yield
    finally:
        os.chdir(previous_cwd)

@contextlib.contextmanager
def as_user(*, uid=None, name=None):
    assert (uid is None) != (name is None)

    if uid is not None:
        pwentry = pwd.getpwuid(uid)
    else:
        pwentry = pwd.getpwnam(name)

    previous_euid = os.geteuid()

    try:
        os.seteuid(pwentry.pw_uid)
    except OSError as error:
        logger.error("Failed to set effective uid: %s", error)
        raise TaskFailed

    with temporary_cwd(pwentry.pw_dir):
        try:
            yield
        finally:
            os.seteuid(previous_euid)

@contextlib.contextmanager
def as_root():
    euid = os.geteuid()
    egid = os.getegid()

    try:
        os.seteuid(0)
        os.setegid(0)
    except OSError as error:
        logger.error("Failed to set effective uid/gid: %s", error)
        raise TaskFailed

    try:
        yield
    finally:
        os.setegid(egid)
        os.seteuid(euid)

def install(*packages):
    logger.info("Installing packages: %s", " ".join(packages))

    env = os.environ.copy()
    env["DEBIAN_FRONTEND"] = "noninteractive"

    with as_root():
        try:
            output = subprocess.check_output(
                ["apt-get", "-qq", "-y", "install"] + list(packages),
                env=env, encoding="utf-8")
        except subprocess.CalledProcessError as error:
            logger.error("Failed to install packages: %s: %s",
                         " ".join(packages), error.output)
            raise TaskFailed

    for line in output.splitlines():
        match = re.match(r"^Setting up ([^ ]+) \(([^)]+)\) \.\.\.", line)
        if match:
            package_name, version = match.groups()
            logger.info("  %s (%s)", package_name, version)

def service(action, name):
    present, past = {
        "start": ("Starting", "Started"),
        "restart": ("Restarting", "Restarted"),
        "reload": ("Reloading", "Reloaded"),
        "stop": ("Stopping", "Stop"),
    }[action]

    try:
        with as_root():
            subprocess.check_output(
                ["service", name, action],
                stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        logger.warning("%s service failed: %s: %s", present, name,
                       error.output.decode().strip())
    else:
        logger.info("%s service: %s", past, name)

