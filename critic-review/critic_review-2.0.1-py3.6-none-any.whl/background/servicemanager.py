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

import argparse
import asyncio
import errno
import glob
import grp
import json
import logging
import os
import pwd
import signal
import stat
import subprocess
import sys
import time

logger = logging.getLogger("background.servicemanager")

import base
import background.service

def process_uptime(pid):
    with open("/proc/stat", "r", encoding="ascii") as proc_stat:
        for line in proc_stat:
            key, _, value = line.strip().partition(" ")
            if key == "btime":
                btime = int(value)
                break
        else:
            btime = None

    with open(f"/proc/{pid}/stat", "r", encoding="ascii") as stat_file:
        items = stat_file.read().split()

    return time.time() - (btime + (int(items[21]) / os.sysconf("SC_CLK_TCK")))

class Service():
    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.task = None
        self.process = None

class ServiceManager(background.service.BackgroundService):
    name = "servicemanager"
    manage_socket = True

    # The master process manages our pid file, so tell our base class to
    # leave it alone.
    manage_pidfile = False

    def __init__(self):
        super(ServiceManager, self).__init__()
        self.services = {
           service_name: Service(service_name, service_data)
           for service_name, service_data in self.settings.services.items()
           if service_name != self.name
        }
        self.service_futures = {}

    async def run_service(self, service):
        def signal_futures(is_running):
            for future in self.service_futures.pop(service.name, []):
                future.set_result(is_running)

        if service.task is not None:
            signal_futures(True)
            return

        service.task = asyncio.Task.current_task()

        logger.info("%s: Starting service", service.name)

        try:
            started = []
            exited = []

            while not self.is_stopping:
                process = await asyncio.create_subprocess_exec(
                    sys.executable, "-m", f"background.{service.name}",
                    stdin=asyncio.subprocess.DEVNULL,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)

                if self.is_stopping:
                    process.terminate()
                    await process.wait()
                    break

                service.process = process

                signal_futures(True)

                logger.info("%s: Started process: pid=%d", service.name,
                            process.pid)

                started.append(self.loop.time())

                stdout, stderr = await process.communicate()

                if stderr:
                    logger.warning(stderr.decode())

                service.process = None

                exited.append(self.loop.time())

                duration = exited[-1] - started[-1]

                logger.info(
                    "%s: Process exited: returncode=%d duration=%.2fs",
                    service.name, process.returncode, duration)

                if process.returncode == 0:
                    break

                if process.returncode > 0:
                    if len(started) >= 3 and started[-3] - exited[1] < 3:
                        logger.info(
                            "%s: Service crashing too frequently; will not "
                            "restart automatically", service.name)
                        break

                if not self.is_stopping:
                    logger.info("%s: Restarting service", service.name)
        except Exception:
            logger.exception("%s: Exception raised while running service",
                             service.name)
        finally:
            service.task = None
            signal_futures(False)

    async def did_start(self):
        logger.info("Starting services")

        startup_futures = []

        for _, service in sorted(self.services.items()):
            pidfile_path = os.path.join(
                self.settings.paths.runtime, service.name + ".pid")
            logger.debug(
                "creating startup sync file: %s.starting", pidfile_path)
            with open(pidfile_path + ".starting", "w") as starting:
                print(time.ctime(), file=starting)
            service_started = self.loop.create_future()
            startup_futures.append(service_started)
            self.service_futures.setdefault(service.name, []).append(
                service_started)
            asyncio.ensure_future(self.run_service(service))

        await asyncio.wait(startup_futures)

        logger.debug("services started")

    async def handle_client_command(self, command):
        logger.debug("client command: %r", command)

        if command.get("query") == "status":
            def process_data(*, process=None, pid=None):
                if process is not None:
                    pid = process.pid
                if pid is not None:
                    return {
                        "uptime": process_uptime(pid),
                        "pid": pid,
                    }
                return {"uptime": None, "pid": None}

            services = {
                "servicemanager": {"module": "background.servicemanager"},
            }

            services["servicemanager"].update(process_data(pid=os.getpid()))

            for service in self.services.values():
                services[service.name] = {
                    "module": f"background.{service.name}"
                }
                services[service.name].update(
                    process_data(process=service.process))

            return {"services": services}

        if command.get("command") == "restart":
            service_name = command.get("service")

            if service_name == "manager":
                self.terminate()
                return {}

            if service_name not in self.services:
                return {
                    "status": "error",
                    "error": f"{service_name}: no such service"
                }

            service = self.services[service_name]
            service_started = self.loop.create_future()

            self.service_futures.setdefault(service_name, []).append(
                service_started)

            if service.task is None:
                asyncio.ensure_future(self.run_service(service))
            elif service.process is not None:
                logger.info("%s: Sending SIGTERM", service_name)
                service.process.terminate()

            is_running = await asyncio.wait_for(
                service_started, command.get("timeout"))

            return {"is_running": is_running}

        return await super(ServiceManager, self).handle_client_command(
            command)

    async def will_stop(self):
        tasks = []

        logger.info("Shutting down")

        for _, service in sorted(self.services.items(), reverse=True):
            if service.process is not None:
                logger.info("%s: Terminating service", service.name)
                service.process.terminate()
            if service.task is not None:
                tasks.append(service.task)

        await asyncio.wait(tasks, timeout=30)

def run_master(startup_timeout):
    configuration = base.configuration()

    pwentry = pwd.getpwnam(configuration["system.username"])
    grentry = grp.getgrnam(configuration["system.groupname"])

    uid = pwentry.pw_uid
    gid = grentry.gr_gid
    home = pwentry.pw_dir

    criticctl = os.path.join(os.path.dirname(sys.executable), "criticctl")

    settings = json.loads(subprocess.check_output([
        criticctl, "settings",
        "get", "services", "paths.runtime"
    ]))

    runtime_dir = settings["paths.runtime"]
    pidfile_path = os.path.join(runtime_dir, "servicemanager.pid")

    if os.path.isfile(pidfile_path):
        print("%s: file exists; daemon already running?" % pidfile_path,
              file=sys.stderr)
        sys.exit(1)

    # Our RUN_DIR (/var/run/critic/IDENTITY) is typically on a tmpfs that gets
    # nuked on reboot, so recreate it with the right access if it doesn't exist.

    def mkdir(path, mode):
        if not os.path.isdir(path):
            if not os.path.isdir(os.path.dirname(path)):
                mkdir(os.path.dirname(path), mode)
            os.mkdir(path, mode)
        else:
            os.chmod(path, mode)
        os.chown(path, uid, gid)

    mkdir(runtime_dir, 0o755 | stat.S_ISUID | stat.S_ISGID)
    mkdir(os.path.join(runtime_dir, "sockets"), 0o755)

    os.environ["HOME"] = home
    os.chdir(home)

    os.setgid(gid)
    os.setuid(uid)

    starting_pattern = os.path.join(os.path.dirname(pidfile_path), "*.starting")

    # Remove any stale/unexpected *.starting files that would otherwise break
    # our startup synchronization.
    for filename in glob.glob(starting_pattern):
        try:
            os.unlink(filename)
        except OSError as error:
            print(error, file=sys.stderr)

    with open(pidfile_path + ".starting", "w") as starting:
        starting.write("%s\n" % time.ctime())

    def wait_for_startup_sync():
        deadline = time.time() + startup_timeout
        while True:
            filenames = glob.glob(starting_pattern)
            if not filenames:
                return 0
            if time.time() > deadline:
                break
            time.sleep(0.1)
        print(file=sys.stderr)
        print(("Startup synchronization timeout after %d seconds!"
                             % startup_timeout), file=sys.stderr)
        print("Services still starting:", file=sys.stderr)
        for filename in filenames:
            print("  " + os.path.basename(filename), file=sys.stderr)
        return 1

    from . import daemon

    with open(pidfile_path, "w") as pidfile:
        daemon.detach(parent_exit_hook=wait_for_startup_sync)
        pidfile.write("%s\n" % os.getpid())

    os.umask(0o22)

    was_terminated = False

    def terminated(signum, frame):
        nonlocal was_terminated
        was_terminated = True

    signal.signal(signal.SIGTERM, terminated)

    while not was_terminated:
        process = subprocess.Popen(
            [sys.executable, "-m", "background.servicemanager", "--slave"],
            encoding="utf-8")

        while not was_terminated:
            try:
                pid, status = os.waitpid(process.pid, os.WNOHANG)
                if pid == process.pid:
                    process = None
                    break
                time.sleep(0.1)
            except OSError as error:
                break

    if process:
        try:
            process.send_signal(signal.SIGTERM)
            process.wait()
        except:
            pass

    try:
        os.unlink(pidfile_path)
    except:
        pass

def main():
    parser = argparse.ArgumentParser()

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument("--slave", action="store_true")
    mode_group.add_argument("--master", action="store_true")

    master_group = parser.add_argument_group("Master mode options")
    master_group.add_argument("--startup-timeout", type=int, default=30)

    arguments = parser.parse_args()

    if arguments.slave:
        background.service.call(ServiceManager)
    else:
        run_master(arguments.startup_timeout)

if __name__ == "__main__":
    main()
