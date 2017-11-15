"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.brew.base import Brew
from tornado import gen
from tornado.iostream import IOStream, StreamClosedError
from tornado.tcpserver import TCPServer
from tornado.netutil import bind_sockets
from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.local import LocalSettings
from uuid import getnode
import socket
try:
    from tornado.netutil import bind_unix_socket
    unix = True
except ImportError:  # pragma no cover
    unix = False

DELIMITER = b'\n\r\n\r'


class LocalBrewPatron(object):
    def __init__(self, sock, brew, patron_id, brewer_id, callback):
        self.brew = brew
        self.patron_id = patron_id
        self.brewer_id = brewer_id
        self.callback = callback

        self.running = True

        if unix and not LocalSettings['use_localhost']:
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        else:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock = (sock[0], sock[1])

        self.stream = IOStream(self.socket)
        self.stream.connect(sock, callback=self._read_data)

    def stop(self, notify=False):
        self.running = False
        self.stream.close()
        if notify:
            self.brew.stop_patron(self.patron_id, None, self.brewer_id)

    @gen.coroutine
    def _read_data(self):  # pragma no cover
        while self.running:
            try:
                data = yield self.stream.read_until(DELIMITER)
                data = data[:-4]
                self.callback(self.brewer_id, data)
            except StreamClosedError:
                self.stop(True)


class LocalBrewServer(TCPServer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = get_logger(self.__class__.__name__)
        self.connected_streams = []

    def handle_stream(self, stream, addr):
        self.connected_streams.append(stream)

    @gen.coroutine
    def write_all(self, data):
        for stream in self.connected_streams:
            try:
                ret = yield stream.write(data)
                if ret is not None:
                    self.connected_streams.remove(stream)
                    self.logger.warn("Unable to write to a stream")
            except StreamClosedError:
                self.connected_streams.remove(stream)


class LocalBrew(Brew):
    def __init__(self, *args, **kwargs):
        self.logger = get_logger(self.__class__.__name__)
        self.name = "local-{}".format(str(getnode()))
        self._patrons = {}
        self._local_servers = {}

        super().__init__(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        return LocalSettings

    def configure(self, context):
        non_casting_types = [type(None), str]
        for setting in LocalSettings.keys():
            if context and setting in context:
                _type = type(LocalSettings[setting])
                if _type in non_casting_types:
                    LocalSettings[setting] = context[setting]
                else:
                    # cast incoming value to known type
                    LocalSettings[setting] = _type(context[setting])

    def start(self):
        self.logger.info("Starting local brew")

    def stop(self):
        self.logger.info("Stopping local brew")
        for brewer_id, patron in self._patrons.items():
            patron.stop()
            del(self._local_servers[brewer_id])

    def create_brewer(self, brewer):
        if brewer.brewer_id not in self._local_servers:
            if unix and not LocalSettings['use_localhost']:
                self.sock_args = '/tmp/{}.sock'.format(brewer.brewer_id)
                sockets = [bind_unix_socket(self.sock_args)]
            else:
                sockets = bind_sockets(0, address='127.0.0.1',
                                       family=socket.AF_INET)
                self.sock_args = ('127.0.0.1', sockets[0].getsockname()[1])

            self._local_servers[brewer.brewer_id] = LocalBrewServer()
            self._local_servers[brewer.brewer_id].add_sockets(sockets)

        details = super().create_brewer(brewer)

        if details is None:
            details = {}

        details.update({
            'sock': self.sock_args,
        })

        brewer.add_brew_alias(self.name, self)

        return details

    def destroy_brewer(self, brewer):
        brewer.remove_brew_alias(self.name)
        if brewer.brewer_id in self._local_servers:
            self._local_servers[brewer.brewer_id].stop()
            del(self._local_servers[brewer.brewer_id])

    def create_patron(self, patron):
        details = super().create_patron(patron)

        if details is None:
            details = {}

        patron.add_brew_alias(self.name, self)

        return details

    def destroy_patron(self, patron):
        patron.remove_brew_alias(self.name)

    def start_patron(self, patron_id, topic, brewer_id, brewer_config,
                     brewer_brew, callback):
        if brewer_id in self._patrons:
            self.logger.info("Already subscribed to the brewer")

        self._patrons[brewer_id] = LocalBrewPatron(brewer_brew['sock'], self,
                                                   patron_id, brewer_id,
                                                   callback)

    def stop_patron(self, patron_id, topic, brewer_id):
        if brewer_id in self._patrons:
            self._patrons[brewer_id].stop()
            del(self._patrons[brewer_id])

    def brew(self, brewer_id, topic, data, patrons):
        if brewer_id in self._local_servers:
            self._local_servers[brewer_id].write_all(data + DELIMITER)
