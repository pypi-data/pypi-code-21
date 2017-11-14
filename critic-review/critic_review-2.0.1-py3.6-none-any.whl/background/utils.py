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

import asyncio
import json
import os
import signal
import stat
import traceback

import api
import base

class ServiceError(Exception):
    pass

class TimeoutError(Exception):
    pass

def issue_command(service_name, command, timeout=None):
    socket_path = os.path.join(
        api.critic.settings().paths.runtime, "sockets", service_name + ".unix")

    try:
        if not stat.S_ISSOCK(os.stat(socket_path).st_mode):
            raise OSError
    except OSError:
        raise ServiceError("Service not running: %s" % service_name)

    loop = asyncio.new_event_loop()

    async def communicate():
        reader, writer = await asyncio.open_unix_connection(
            socket_path, loop=loop)

        writer.write(json.dumps(command).encode())
        writer.write_eof()

        data = await reader.read()

        return json.loads(data.decode())

    try:
        return loop.run_until_complete(asyncio.wait_for(
            communicate(), timeout, loop=loop))
    except asyncio.TimeoutError:
        raise TimeoutError()
    finally:
        loop.close()

def wakeup(service_name):
    import api
    pidfile_path = os.path.join(api.critic.settings().paths.runtime,
                                service_name + ".pid")
    try:
        with open(pidfile_path, "r", encoding="ascii") as pidfile:
            pid = int(pidfile.read().strip())
        os.kill(pid, signal.SIGHUP)
    except Exception:
        # Print traceback to stderr.  Might end up in web server's error log,
        # where it has a chance to be noticed.
        traceback.print_exc()
