"""
Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import logging
from tornado import gen, websocket


class ConnectionPool(object):
    def __init__(self):
        self._logger = \
            logging.getLogger('pubkeeper.server.websocket.ConnectionPool')
        self._connections = []
        self._lvc = None

    @gen.coroutine
    def add_socket(self, socket):
        if self._lvc is not None:
            self._logger.debug("Sending LVC data")
            yield socket.write_message(self._lvc, binary=True)

        self._connections.append(socket)

    def del_socket(self, socket):
        # make sure socket is in the collection since it can be removed also
        # as a result of an exception during a publish op.
        if socket in self._connections:
            self._connections.remove(socket)

    def empty(self):
        return len(self._connections) == 0

    def invalidate(self):
        self._lvc = None

    @gen.coroutine
    def publish(self, data, ignore=None):
        self._lvc = data

        for conn in self._connections:
            if ignore is None or ignore is not conn:
                try:
                    yield conn.write_message(data, binary=True)
                except websocket.WebSocketClosedError:
                    # If this connection is dead, remove it
                    self._logger.warning("WebSocketClosedError exception")
                    self.del_socket(conn)
