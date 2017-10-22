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


from gi.repository import GObject

from . import _client, _request


class ClientGLib(_client.Client, GObject.GObject):
    """
    Adds GLib scheduling and signal functionality to Client.

    GLib signals:
      client-connected
      client-disconnected(reason)
    """

    __gsignals__ = {
        'client-connected': (GObject.SIGNAL_RUN_FIRST, None, ()),
        'client-disconnected': (GObject.SIGNAL_RUN_FIRST, None, (int, str)),
    }

    def __init__(self, *, excepthook=None):
        GObject.GObject.__init__(self)
        super().__init__(excepthook=excepthook)
        self.executor.connect_loop(self._connected_cb, self._disconnected_cb)

    def _connected_cb(self):
        self.emit('client-connected')

    def _disconnected_cb(self, reason, message):
        self.emit('client-disconnected', reason, message)


class ServerPropertiesGLib(_client.ServerProperties, GObject.GObject):
    """
    Adds GLib property and signal functionality to ServerProperties.

    Assignment to volume, elapsed and option-X is reflected in the server.

    GLib signals:
      server-error(message)
    """
    current_song = GObject.property()
    status = GObject.property()
    state = GObject.property(type=str)
    volume = GObject.property(type=int)
    time = GObject.property(type=int)
    elapsed = GObject.property(type=float)
    bitrate = GObject.property(type=str)
    updating_db = GObject.property(type=str)

    for option in _client.ServerProperties.OPTION_NAMES:
        locals()['option_' + option] = GObject.property(type=bool, default=False)

    __gsignals__ = {
        'server-error': (GObject.SIGNAL_RUN_FIRST, None, (str,)),
    }

    def __init__(self, client):
        GObject.GObject.__init__(self)
        self.notify_handlers = []
        self.notify_handlers.append(self.connect('notify::volume', self.notify_volume_cb))
        self.notify_handlers.append(self.connect('notify::elapsed', self.notify_elapsed_cb))
        for option in self.OPTION_NAMES:
            self.notify_handlers.append(self.connect('notify::option-' + option, self.notify_option_cb))
        super(ServerPropertiesGLib, self).__init__(client)

    def _block(self):
        for handler in self.notify_handlers:
            self.handler_block(handler)
        self.freeze_notify()

    def _unblock(self):
        self.thaw_notify()
        for handler in self.notify_handlers:
            self.handler_unblock(handler)

    def _status_updated(self):
        super()._status_updated()
        if 'error' in self.status:
            self.emit('server-error', self.status['error'])
            _client.Task(self.ampd.clearerror())

    @staticmethod
    def notify_volume_cb(self, param):
        self._set_server_volume()

    @staticmethod
    @_client.task
    async def notify_elapsed_cb(self, param):
        await self.ampd.seekcur(self.elapsed)

    @staticmethod
    @_client.task
    async def notify_option_cb(self, param):
        option = param.name.split('-')[1]
        await getattr(self.ampd, option)(int(self.get_property(param.name)))
