# coding: utf-8

# Asynchronous Music Player Daemon client library for Python

# Copyright (C) 2015 Itaï BEN YAACOV

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import os
import logging
import asyncio
import urllib.parse
import sys
import decorator

from . import _request, errors


_logger = logging.getLogger(__name__.split('.')[0])


class Task(asyncio.Task):
    def __init__(self, future):
        self._future = future
        super().__init__(self.wrap())
        asyncio.ensure_future(self)

    async def wrap(self):
        try:
            await self._future
        except (asyncio.CancelledError, errors.DisconnectError):
            pass
        except:
            print('While awaiting {}:'.format(self._future))
            sys.excepthook(*sys.exc_info())

    def __repr__(self):
        return "Task({})".format(repr(self._future))


@decorator.decorator
def task(func, *args, **kwargs):
    """
    Decorator for AMPD task functions.

    Makes a coroutine execute immediately via asyncio.ensure_future, ignoring cancellation and diconnect errors.
    """
    return Task(func(*args, **kwargs))


class Executor(object):
    """
    Generates AMPD requests.
    """

    def __init__(self, client_or_parent):
        if isinstance(client_or_parent, Executor):
            self._parent = client_or_parent
            self._client = client_or_parent._client
            self._parent._children.append(self)
        else:
            self._parent = None
            self._client = client_or_parent
        self._children = []
        self._tasks = []

    async def close(self):
        _logger.debug("Closing executor {}".format(self))
        if not self._client:
            return
        while self._children:
            await self._children[0].close()
        if self._tasks:
            for task in self._tasks:
                task.cancel()
            await asyncio.wait(self._tasks)
        if self._parent:
            self._parent._children.remove(self)
            self._parent = None
        self._client = None
        _logger.debug("Executor closed")

    def sub_executor(self):
        "Return a child Executor."
        return Executor(self)

    @task
    async def connect_loop(self, connected_cb=None, disconnected_cb=None):
        """
        Convenience function for hooking into connect and disconnect events.
        Calls connected_cb() upon connect and disconnected_cb(reason, message) upon disconnect.
        """
        while True:
            try:
                await self.idle(_request.Event.CONNECT)
                _logger.debug("Connected")
                connected_cb and connected_cb()
                await self.idle(_request.Event.NONE)
            except errors.DisconnectError as e:
                _logger.debug("Connect loop disconnected")
                disconnected_cb and disconnected_cb(e.reason, e.message)

    def get_is_connected(self):
        return self._client.is_connected

    def get_protocol_version(self):
        return self._client.protocol_version

    def __getattr__(self, name):
        return _request.Request._new_request(self, name)

    def _log_request(self, request):
        if self._client is None:
            raise errors.DisconnectError(Client.DISCONNECT_SHUTDOWN, None)
        task = asyncio.Task.current_task()
        _logger.debug("Appending task {} to {}".format(task, self))
        self._tasks.append(task)
        request.add_done_callback(lambda f: self._tasks.remove(task))
        if isinstance(request, _request.RequestPassive):
            self._client._wait(request)
        else:
            self._client._send(request)


class Client(object):
    """
    Establishes connection with the MPD server.
    """

    DISCONNECT_NOT_CONNECTED = 0
    DISCONNECT_FAILED_CONNECT = 1
    DISCONNECT_ERROR = 2
    DISCONNECT_REQUESTED = 3
    DISCONNECT_RECONNECT = 4
    DISCONNECT_SHUTDOWN = 5
    DISCONNECT_PASSWORD = 6

    def __init__(self, *, excepthook=None):
        """
        Initialize a client.

        excepthook - override sys.excepthook for exceptions raised in workers.
        """
        self.executor = Executor(self)
        self._excepthook = excepthook
        self._waiting_list = []
        self._host = self._port = self._password = None

        self.is_connected = False
        self.protocol_version = None
        self._running = None

    def __del__(self):
        _logger.debug("Deleting {}".format(self))

    async def close(self):
        """
        Close all workers and worker groups, disconnect from server.
        """
        _logger.debug("Closing client")
        await self.executor.close()
        await self.disconnect_from_server(self.DISCONNECT_SHUTDOWN)
        _logger.debug("Client closed")

    async def connect_to_server(self, host=None, port=6600, password=None):
        """
        host     - '[password@]hostname[:port]'.  Default to $MPD_HOST or 'localhost'.
        port     - Ignored if given in the 'host' argument.
        password - Ignored if given in the 'host' argument.
        """

        netloc = urllib.parse.urlsplit('//' + (host or os.environ.get('MPD_HOST', 'localhost')))

        self._host = netloc.hostname
        self._port = netloc.port or port
        self._password = netloc.username or password

        await self.reconnect_to_server()

    async def reconnect_to_server(self):
        """
        Connect to server with previous host / port / password.
        """
        self._run()

    async def disconnect_from_server(self, _reason=DISCONNECT_REQUESTED, _message=None):
        if self._running:
            self._running.disconnect = errors.DisconnectError(_reason, _message)
            self._running.cancel()
            await asyncio.wait_for(self._running, None)

    @task
    async def _run(self):
        await self.disconnect_from_server(self.DISCONNECT_RECONNECT)
        self._running = asyncio.Task.current_task()
        try:
            self._active_queue = []
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
            welcome = _request.RequestWelcome(self.executor)
            self._active_queue = [welcome]
            self._connect_task(welcome)
            self._is_idle = False
            while True:
                if self._active_queue:
                    request = self._active_queue.pop(0)
                    await request._read(self._reader)
                else:
                    self._active = False
                    await asyncio.sleep(0)
                    if self._active or self._event(_request.Event.IDLE, True):
                        continue
                    self._idle_task()
        except asyncio.CancelledError:
            pass
        except OSError as exc:
            if self.is_connected:
                self._running.disconnect = errors.DisconnectError(self.DISCONNECT_ERROR, str(exc))
            else:
                self._running.disconnect = errors.DisconnectError(self.DISCONNECT_FAILED_CONNECT, str(exc))
        finally:
            self.is_connected = False
            self.protocol_version = None
            for request in self._active_queue + self._waiting_list:
                if not request.done():
                    request.set_exception(self._running.disconnect)
            self._running = None
            del self._active_queue

    def _send(self, request):
        self._active = True
        if not self.is_connected:
            raise errors.DisconnectError(self.DISCONNECT_NOT_CONNECTED, None)
        if isinstance(request, _request.RequestIdle):
            self._is_idle = True
        elif self._is_idle:
            self._writer.write(b'noidle\n')
            _logger.debug("Unidle")
            self._is_idle = False
        self._writer.write(request._commandline.encode('utf-8') + b'\n')
        _logger.debug("Write : " + request._commandline)
        self._active_queue.append(request)

    def _wait(self, request):
        self._active = True
        event = self._current_events() & request._event_mask
        if event:
            request.set_result(event)
        else:
            self._waiting_list.append(request)
            request.add_done_callback(self._waiting_list.remove)

    def _current_events(self):
        return (_request.Event.IDLE if self.is_connected and self._is_idle else 0) | (_request.Event.CONNECT if self.is_connected else 0)

    @task
    async def _connect_task(self, welcome):
        self.protocol_version = await welcome
        self.is_connected = True
        if self._password:
            try:
                await self.executor.password(self._password)
            except errors.ReplyError:
                self.disconnect_from_server(self.DISCONNECT_PASSWORD)
                return
        self._event(_request.Event.CONNECT)

    def _unidle(self, request):
        self._is_idle = False

    @task
    async def _idle_task(self):
        _logger.debug("Going idle")
        request = _request.RequestIdle(self.executor)
        request.add_done_callback(self._unidle)
        event = sum(_request.Event[subsystem.upper()] for subsystem in await request)
        if event:
            self._event(event)

    def _event(self, event, one=False):
        for request in list(self._waiting_list):
            reply = request._event_mask & event
            if reply:
                self._active = True
                request.set_result(reply)
                if one:
                    return True
        return False


class ServerProperties(object):
    """
    Keeps track of various properties of the server:
    - status
    - current_song
    - state
    - volume
    - time
    - elapsed
    - bitrate
    - option-X, for X in consume, random, repeat, single

    Assignment to volume is reflected in the server.

    Do not use this -- use ServerPropertiesGLib instead.
    """

    OPTION_NAMES = ['consume', 'random', 'repeat', 'single']

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, value):
        self._volume = value
        if not self._blocking:
            self._set_server_volume()

    @task
    async def _set_server_volume(self):
        if self._setting_volume:
            self._setting_volume.cancel()
        self._setting_volume = asyncio.Task.current_task()
        value = self.volume
        _logger.debug("Setting voume to {} at {}".format(value, id(self._setting_volume)))
        try:
            while True:
                try:
                    await self.ampd.setvol(value)
                except errors.ReplyError:
                    await self.ampd.idle(_request.Event.PLAYER)
                    continue
                status = await self.ampd.status()
                if int(status['volume']) == value:
                    break
                await self.ampd.idle(_request.Event.PLAYER | _request.Event.MIXER)
            _logger.debug("Success")
        finally:
            self._setting_volume = None

    def __init__(self, client):
        self.ampd = client.executor.sub_executor()
        self.ampd.connect_loop(self._connected_cb, self._disconnected_cb)
        self._setting_volume = None
        self._reset()

    def _block(self):
        self._blocking = True

    def _unblock(self):
        self._blocking = False

    def _reset(self):
        self._block()
        self._error = None
        self.current_song = {}
        self.status = {}
        self.state = ''
        self.volume = -1
        self.time = 0
        self.elapsed = 0
        self.bitrate = None
        self.updating_db = None
        self._unblock()

    @task
    async def _connected_cb(self):
        while True:
            self._block()
            self.status = await self.ampd.status()
            self._status_updated()
            if self.state == 'stop':
                if self.current_song:
                    self.current_song = {}
            else:
                new_current_song = await self.ampd.currentsong()
                if self.current_song != new_current_song:
                    self.current_song = new_current_song
            self._unblock()
            await self.ampd.idle(_request.Event.PLAYER | _request.Event.MIXER | _request.Event.OPTIONS | _request.Event.UPDATE, timeout=(int(self.elapsed + 1.5) - self.elapsed) if self.state == 'play' else None)

    def _status_properties(self):
        properties = {name: self.status.get(name) for name in ('state', 'bitrate', 'updating_db')}
        volume = int(self.status['volume'])
        if not self._setting_volume and volume != -1:
            properties['volume'] = volume
        if 'time' in self.status:
            times = self.status['time'].split(':')
            properties['time'] = int(times[1])
            properties['elapsed'] = float(self.status['elapsed'])
        else:
            properties['time'] = 0
            properties['elapsed'] = 0.0
        for name in self.OPTION_NAMES:
            properties['option_' + name] = bool(int(self.status[name]))
        return properties

    def _status_updated(self):
        for key, value in self._status_properties().items():
            if getattr(self, key) != value:
                setattr(self, key, value)

    def _disconnected_cb(self, reason, message):
        _logger.debug("Server properties disconnected.")
        self._reset()
