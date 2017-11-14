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

import asyncio
import collections
import datetime
import functools
import io
import json
import logging
import logging.handlers
import os
import pickle
import signal
import struct
import sys

logger = logging.getLogger(__name__)

import api

class AdministratorMailHandler(logging.Handler):
    def __init__(self, logfile_path):
        super(AdministratorMailHandler, self).__init__()
        self.logfile_name = os.path.basename(logfile_path)

    def emit(self, record):
        import api
        import mailutils
        with api.critic.startSession(for_system=True) as critic:
            message = self.formatter.format(record)
            mailutils.sendAdministratorErrorReport(
                critic.database, self.logfile_name, message.splitlines()[0],
                message)

class SetContextFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, "context"):
            record.context = record.name
        if not hasattr(record, "stacktrace"):
            record.stacktrace = ""
        return True

class ClientReader():
    def __init__(self):
        self.data = asyncio.Future()

    async def read(self, timeout=None):
        return await asyncio.wait_for(self.data, timeout)

class ClientWriter():
    def __init__(self, transport):
        self.transport = transport
        self.closed = asyncio.Future()

    def write(self, data):
        self.transport.write(data)

    async def close(self, timeout=None):
        self.transport.close()
        return await asyncio.wait_for(self.closed, timeout)

class ClientProtocol(asyncio.Protocol):
    def __init__(self, service):
        self.service = service
        self.reader = None
        self.writer = None
        self.buffer = io.BytesIO()

    def connection_made(self, transport):
        self.reader = ClientReader()
        self.writer = ClientWriter(transport)
        asyncio.ensure_future(
            self.service.client_connected(self, self.reader, self.writer))

    def connection_lost(self, exception):
        self.writer.closed.set_result(True)
        asyncio.ensure_future(
            self.service.client_disconnected(self, exception))

    def data_received(self, data):
        self.buffer.write(data)

    def eof_received(self):
        self.reader.data.set_result(self.buffer.getvalue())
        return True

class WorkerError(Exception):
    def __init__(self, returncode, output):
        super(WorkerError, self).__init__("Worker process failed")
        self.returncode = returncode
        self.output = output

class WorkerForRequest():
    def __init__(self, loop, coroutine):
        self.loop = loop
        self.task = asyncio.ensure_future(coroutine)
        self.task.add_done_callback(self.update_timestamp)
        self.timestamp = loop.time()

    def update_timestamp(self, task):
        assert task is self.task
        self.timestamp = self.loop.time()

class MaintenanceWork():
    minimum_gap = 12 * 60 * 60  # 12 hours

    def __init__(self, loop, callback, hours, minutes):
        self.loop = loop
        self.callback = callback
        self.hours = hours
        self.minutes = minutes
        self.timestamp = self.loop.time()

    @property
    def should_run(self):
        if self.timestamp:
            if self.loop.time() - self.timestamp < self.minimum_gap:
                return False
        now = datetime.datetime.now()
        if now.hour < self.hours:
            return False
        if now.hour == self.hours and now.minutes < self.minutes:
            return False
        return True

    def run(self):
        def on_done(task):
            try:
                task.result()
            except Exception:
                logger.exception("Maintenance work failed")
            self.timestamp = self.loop.time()
        task = asyncio.ensure_future(self.callback())
        task.add_done_callback(on_done)
        return task

class WorkerAllocation():
    def __init__(self, item, running, semaphore):
        self.item = item
        self.running = running
        self.semaphore = semaphore

    async def __aenter__(self):
        await self.semaphore.acquire()
        self.running.add(self.item)
        return self

    async def __aexit__(self, *exc_info):
        self.running.remove(self.item)
        self.semaphore.release()
        return False

class BackgroundServiceCallbacks():
    """Callbacks that BackgroundService sub-classes can override.

    The function type of overriding methods (`def` vs `async def`) must match
    the declarations in this interface.
    """

    def will_start(self):
        """Called before the service starts.

        If a false value is returned, the service exits immediately with a
        zero exit status, meaning it will be disabled.

        Logging is set up and |self.settings| contains all system settings, but
        nothing else will have been done.
        """
        return True
    async def did_start(self):
        """Called after all startup operations have been performed.

        This is an appropriate time to e.g. register maintenance work.
        """
        pass
    async def handle_client(self, reader, writer):
        """Called to handle a client connection

        This method should communicate with the client using the |reader| and
        |writer| objects.

        The default implementation reads a single JSON object, passes it to
        |handle_client_command()|, writes the response back to the client and
        closes the connection.
        """
        pass
    async def handle_client_command(self, command):
        """Called to handle a command from a client

        This method should return a response that will then be sent back to the
        client that issued the command.

        The default implementation handles commands containing a list of
        requests, by starting one worker per request.
        """
        pass
    async def will_run_worker(self, request):
        """Called before a worker child process is started to handle a request.

        If this method returns a value (not None) that value is used as the
        response to the request, and no child process is started.
        """
        pass
    async def did_run_worker(self, request):
        """Called after a worker child process has finished."""
        pass
    async def wake_up(self):
        """Called when a SIGHUP has been received."""
        pass
    async def will_stop(self):
        """Called when SIGTERM has been received, before the event loop stops.

        This function can perform asynchronous operations, but should of course
        not delay too long."""
        pass
    def did_stop(self):
        """Called when the event loop has stopped."""
        pass

class BackgroundService(BackgroundServiceCallbacks):
    send_administrator_mails = True
    manage_pidfile = True
    manage_socket = False
    default_max_workers = 1

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.loop.set_debug(True)
        self.server = None
        self.requests = {}
        self.running_workers = set()
        self.pending_workers = set()
        self.maintenance_tasks = []
        self.connected_clients = set()
        self.is_terminating = False
        self.is_stopping = False

        self.__wake_up_task = None  # Current asyncio.Task calling wake_up()
        self.__wake_up_call = None  # Handle for delayed call to wake_up()
        self.__wake_up_again = False

    @classmethod
    def pidfile_path(cls):
        return os.path.join(cls.settings.paths.runtime, cls.name + ".pid")

    @classmethod
    def logfile_path(cls):
        return os.path.join(cls.settings.paths.logs, cls.name + ".log")

    @classmethod
    def socket_path(cls):
        return os.path.join(
            cls.settings.paths.runtime, "sockets", cls.name + ".unix")

    @classmethod
    def loglevel(cls):
        loglevel_name = cls.service_data.get("loglevel")
        if loglevel_name is not None:
            return getattr(logging, loglevel_name.upper())
        if cls.settings.system.is_debugging:
            return logging.DEBUG
        return logging.INFO

    @classmethod
    def configure_logging(cls):
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)5s - %(context)s: "
            "%(message)s%(stacktrace)s")

        handler = logging.handlers.RotatingFileHandler(
            cls.logfile_path(), maxBytes=1024**2, backupCount=5)

        handler.setFormatter(formatter)
        handler.setLevel(cls.loglevel())
        handler.addFilter(SetContextFilter())

        root_logger = logging.getLogger()
        root_logger.setLevel(cls.loglevel())
        root_logger.addHandler(handler)

        if cls.send_administrator_mails:
            mail_handler = AdministratorMailHandler(cls.logfile_path())
            mail_handler.setFormatter(formatter)
            mail_handler.setLevel(logging.WARNING)
            root_logger.addHandler(mail_handler)

        logging.getLogger("asyncio").setLevel(logging.ERROR)

    def request_key(self, request):
        return frozenset(request.items())

    def schedule_request(self, request):
        request_key = self.request_key(request)
        if request_key not in self.requests:
            schedule_cleanup = not self.requests
            self.requests[request_key] = WorkerForRequest(
                self.loop, self.run_worker_for_request(request))
            if schedule_cleanup:
                self.schedule_cleanup()
        return self.requests[request_key].task

    def handle_connection(self):
        return ClientProtocol(self)

    async def client_connected(self, client, reader, writer):
        logger.debug("client_connected")

        this_task = asyncio.Task.current_task()

        self.connected_clients.add(this_task)

        try:
            await self.handle_client(reader, writer)
        finally:
            self.connected_clients.remove(this_task)

    async def handle_client(self, reader, writer):
        this_task = asyncio.Task.current_task()

        self.connected_clients.add(this_task)

        response = {
            "status": "ok"
        }

        try:
            command = json.loads((await reader.read()).decode())
        except ValueError as error:
            response.update({
                "status": "error",
                "error": "invalid input",
                "details": str(error)
            })
        else:
            logger.debug("command: %r", command)

            try:
                response.update(await self.handle_client_command(command))
            except asyncio.TimeoutError:
                response.update({
                    "status": "timeout",
                    "timeout": command["timeout"],
                })
            except Exception:
                logger.exception("handle_client_command() crashed")
        finally:
            writer.write(json.dumps(response).encode())
            await writer.close()

    async def handle_client_command(self, command):
        if "requests" in command:
            tasks = [
                self.schedule_request(request)
                for request in command["requests"]
            ]

            if command.get("async"):
                return {}

            logger.debug("waiting for %d tasks", len(tasks))

            done, pending = await asyncio.wait(
                tasks, timeout=command.get("timeout"))

            logger.debug("result: done=%r, pending=%r", done, pending)

            def task_result(task):
                if not task.done():
                    return None
                exception = task.exception()
                if exception is None:
                    return {"success": task.result()}
                return {"failure": str(task.exception())}

            return {
                "done": len(done),
                "pending": len(pending),
                "results": [task_result(task) for task in tasks],
            }

        return {
            "status": "error",
            "error": f"invalid command: {command!r}"
        }

    async def client_disconnected(self, client, exception):
        logger.debug("client_disconnected")

    def worker_allocation(self):
        return WorkerAllocation(
            asyncio.Task.current_task(), self.running_workers,
            self.worker_semaphore)

    async def write_worker_stdin(self, writer, stdin_data):
        writer.write(stdin_data)
        writer.close()

    async def read_worker_stdout(self, reader):
        return await reader.read()

    async def read_worker_stderr(self, reader):
        child_logger = logging.getLogger(__name__ + "[child]")
        while True:
            header = await reader.read(4)
            if not header:
                return
            size, = struct.unpack("=I", header)
            pickled = await reader.read(size)
            record = pickle.loads(pickled)
            child_logger.handle(record)

    async def run_worker(self, *args, module=None, stdin_data=None):
        if module is None:
            if hasattr(self, "worker_module"):
                module = self.worker_module
            else:
                module = f"background.{self.name}"

        if not stdin_data:
            stdin_mode = asyncio.subprocess.DEVNULL
        else:
            stdin_mode = asyncio.subprocess.PIPE

        async with self.worker_allocation():
            logger.debug("starting subprocess: %r", args)

            process = await asyncio.create_subprocess_exec(
                sys.executable, "-m", module, "--worker", *args,
                stdin=stdin_mode,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE)

            logger.debug("worker started: %d", process.pid)

            subtasks = [
                self.read_worker_stdout(process.stdout),
                self.read_worker_stderr(process.stderr)
            ]
            if stdin_data:
                subtasks.append(
                    self.write_worker_stdin(process.stdin, stdin_data))

            stdout, _, _ = await asyncio.gather(*subtasks)

            await process.wait()

        logger.debug("worker process exited: %d => %d",
                     process.pid, process.returncode)

        if process.returncode != 0:
            raise WorkerError(process.returncode, stdout)

        return stdout

    async def run_worker_for_request(self, request):
        value = await self.will_run_worker(request)

        if value is not None:
            logger.debug("skipping request: %r", request)
            return value

        logger.debug("starting worker for request: %r", request)

        stdout = await self.run_worker(
            stdin_data=json.dumps(request).encode())

        logger.debug("worker output: %r", stdout)

        return json.loads(stdout.decode())

    def is_idle(self):
        if self.running_workers:
            logger.debug("not idle: %d running workers",
                         len(self.running_workers))
            return False
        if self.pending_workers:
            logger.debug("not idle: %d pending workers",
                         len(self.pending_workers))
            return False
        if self.connected_clients:
            logger.debug("not idle: %d connected clients",
                         len(self.connected_clients))
            return False
        if self.__wake_up_task:
            return False
        return True

    async def wait_for_idle(self, run_maintenance, *, timeout=None):
        busy_filename = self.pidfile_path() + ".busy"
        assert os.path.isfile(busy_filename)
        if not self.is_idle():
            logger.debug("waiting for idle state")
            deadline = self.loop.time() + timeout if timeout else None
            while not self.is_idle():
                timeout = (max(0, deadline - self.loop.time())
                           if deadline else None)
                if self.running_workers:
                    logger.debug("waiting for %d running workers",
                                 len(self.running_workers))
                    await asyncio.wait(self.running_workers, timeout=timeout)
                elif self.pending_workers:
                    logger.debug("waiting for %d pending workers",
                                 len(self.pending_workers))
                    await asyncio.wait(self.pending_workers, timeout=timeout)
                elif self.connected_clients:
                    logger.debug("waiting for %d connected clients",
                                 len(self.connected_clients))
                    await asyncio.wait(self.connected_clients, timeout=timeout)
                elif self.__wake_up_task:
                    logger.debug("waiting for wake_up() task: %r", timeout)
                    await asyncio.wait_for(self.__wake_up_task, timeout)
                if timeout == 0 and not self.is_idle():
                    logger.warning("timeout waiting for idle state")
                    return False
                await asyncio.sleep(0)
            logger.debug("idle state achieved")
        if run_maintenance and self.maintenance_tasks:
            logger.info("Running maintenance work (forced)")
            await asyncio.wait([
                maintenance_work.run()
                for maintenance_work in self.maintenance_tasks
            ])
        logger.info("Reporting idle state")
        os.unlink(busy_filename)
        return True

    async def stop(self):
        self.is_stopping = True
        await self.will_stop()
        self.loop.stop()

    def do_wake_up(self):
        def wake_up_task_done(task):
            assert task is self.__wake_up_task
            self.__wake_up_task = None
            try:
                delay = task.result()
                if delay is not None:
                    logger.debug("scheduling wake up in %.2fs", delay)
                    self.__wake_up_call = self.loop.call_later(
                        delay, self.do_wake_up)
            except Exception:
                logger.exception("wake_up() crashed")
            if self.__wake_up_again:
                self.loop.call_soon(self.do_wake_up)
                self.__wake_up_again = False

        if self.__wake_up_call:
            self.__wake_up_call.cancel()
            self.__wake_up_call = None

        if self.__wake_up_task:
            self.__wake_up_again = True
            return

        self.__wake_up_task = asyncio.ensure_future(self.wake_up())
        self.__wake_up_task.add_done_callback(wake_up_task_done)

    def interrupt(self):
        logger.debug("interrupt")
        self.loop.call_soon(self.do_wake_up)

    def terminate(self):
        logger.debug("terminate")
        self.is_terminating = True
        asyncio.ensure_future(self.stop())

    def synchronize(self, run_maintenance):
        logger.info("Synchronizing")
        asyncio.ensure_future(self.wait_for_idle(run_maintenance))

    def cleanup(self):
        def keep_worker(worker, now):
            if not worker.task.done():
                logger.debug("  keeping worker: not done")
                return True
            age = now - worker.timestamp
            if age < 30:
                logger.debug("  keeping worker: age=%.1f", age)
                return True
            logger.debug("  purging worker: age=%.1fs", age)
            return False
        now = self.loop.time()
        logger.debug("cleanup: %d requests", len(self.requests))
        self.requests = {
            request: worker
            for request, worker in self.requests.items()
            if keep_worker(worker, now)
        }
        self.schedule_cleanup()

    def schedule_cleanup(self):
        if self.requests:
            self.loop.call_later(10, self.cleanup)

    def check_maintenance(self):
        for maintenance_work in self.maintenance_tasks:
            if maintenance_work.should_run:
                maintenance_work.run()
        self.loop.call_later(300, self.check_maintenance)

    def register_maintenance(self, callback, hours, minutes):
        assert asyncio.iscoroutinefunction(callback)

        if not self.maintenance_tasks:
            self.loop.call_soon(self.check_maintenance)

        self.maintenance_tasks.append(MaintenanceWork(
            self.loop, callback, hours, minutes))

    def __startup_finished(self, disabled):
        starting_filename = self.pidfile_path() + ".starting"
        if os.path.isfile(starting_filename):
            logger.debug("deleting startup sync file: %s", starting_filename)
            os.unlink(starting_filename)
        if not disabled:
            self.do_wake_up()

    async def start(self):
        logger.info("Starting service")

        self.loop.add_signal_handler(signal.SIGHUP, self.interrupt)
        self.loop.add_signal_handler(signal.SIGTERM, self.terminate)
        self.loop.add_signal_handler(signal.SIGUSR1, functools.partial(
            self.synchronize, run_maintenance=False))
        self.loop.add_signal_handler(signal.SIGUSR2, functools.partial(
            self.synchronize, run_maintenance=True))

        max_workers = self.service_data.get("max_workers")
        if max_workers is None:
            max_workers = self.default_max_workers
        self.worker_semaphore = asyncio.BoundedSemaphore(max_workers)

        if self.manage_pidfile:
            with open(self.pidfile_path(), "w") as pidfile:
                print(os.getpid(), file=pidfile)

        if self.manage_socket:
            logger.info(f"Listening at: {self.socket_path()}")
            self.server = await self.loop.create_unix_server(
                self.handle_connection, self.socket_path())

        asyncio.ensure_future(self.did_start()).add_done_callback(
            lambda task: self.__startup_finished(False))

    def run(self):
        if not self.will_start():
            logger.info("Service disabled")
            self.__startup_finished(True)
            return

        self.loop.run_until_complete(self.start())

        logger.debug("running loop")

        try:
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        except BaseException:
            logger.exception("run_forever() threw an exception")

        logger.debug("loop stopped")

        if self.server:
            self.server.close()
            self.loop.run_until_complete(self.server.wait_closed())

        self.loop.close()

        self.did_stop()

        if self.is_terminating:
            logger.debug("sending SIGTERM to self")

            self.loop.remove_signal_handler(signal.SIGTERM)
            os.kill(os.getpid(), signal.SIGTERM)

def call(service_class, *args, **kwargs):
    with api.critic.startSession(for_system=True) as critic:
        settings = critic.settings

    service_class.settings = settings
    service_class.service_data = settings.services[service_class.name]

    service_class.configure_logging()

    try:
        service = service_class(*args, **kwargs)
    except Exception:
        logger.exception("Service factory failed")
        return

    logger.debug("starting service")

    try:
        service.run()
    except Exception:
        logger.exception("Service running failed")
        return

    logger.debug("service stopped")
