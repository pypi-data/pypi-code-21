"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import ioloop


class PubkeeperCommunicationHandler(object):  # pragma: no cover
    def __init__(self, *args, io_loop=None, handler_args=None, **kwargs):
        self._handler_args = handler_args
        if io_loop is None:
            self._ioloop = ioloop.IOLoop.current()
        else:
            self._ioloop = io_loop

        super().__init__(*args, **kwargs)

    def shutdown(self):
        """shutdown

        Shutdown the connection.
        """
        raise NotImplementedError()

    def write_message(self, msg):
        """write_message
        Take a bytes like string and write it to the specific transport

        Args:
            msg (bytes) - Data to write
        """
        raise NotImplementedError()

    def connect(self):
        """connect

        Any potential connection handling necessary for this handler
        """
        pass

    def on_connected(self):
        """on_connected

        Called when a connection is established to the other end
        """
        pass

    def on_message(self, msg):
        """on_message

        Handler for when the handler receives a message from the other end.
        This may implenet a queue for processing, so end users who are iterating
        over read_messages will block waiting for the next available msg.
        """
        raise NotImplementedError()

    def on_disconnected(self):
        """on_disconnected

        Called when the connection to the other end is terminated
        """
        pass
