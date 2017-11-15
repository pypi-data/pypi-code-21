"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import ioloop
from pubkeeper.utils.websocket import WebsocketConnection
from threading import Thread


class WebsocketPatron(object):
    def __init__(self, topic, brewer_brew, callback, protocol):
        self._topic = topic
        self._brewer_brew = brewer_brew
        self._callback = callback

        self._protocol = protocol
        self._ioloop = None
        self._socket = None
        self._connection = None
        self._th = None

    def start(self):
        self._th = Thread(target=self.run)
        self._th.start()

    def run(self):
        self._ioloop = ioloop.IOLoop()
        self._ioloop.make_current()

        self._socket = WebsocketConnection({
            'host': self._brewer_brew['hostname'],
            'port': self._brewer_brew['port'],
            'resource': '',
            'secure': self._brewer_brew['secure'],
            'headers': None
        })
        self._socket.start(on_connected=self.on_connected,
                           on_message=self.on_message)

        self._ioloop.start()
        self._ioloop.close()
        self._ioloop = None

    def on_message(self, data):
        brewer_id, data = self._protocol.unpackage_data(data)
        self._callback(brewer_id, data)

    def on_connected(self, connection):
        self._connection = connection
        self._protocol.on_connected(self._connection, self._topic)

    def stop(self):
        # This is called from outside our thread, and we need this
        # thread to shut it self down on the next iteration
        if self._ioloop:
            self._ioloop.add_callback(self._stop)
        if self._th:
            self._th.join(5)
            self._th = None

    def _stop(self):
        self._protocol.on_disconnected(self._connection, self._topic)
        self._socket.stop()
        self._ioloop.stop()

    @property
    def started(self):
        return self._th is not None

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, protocol):
        self._protocol = protocol
