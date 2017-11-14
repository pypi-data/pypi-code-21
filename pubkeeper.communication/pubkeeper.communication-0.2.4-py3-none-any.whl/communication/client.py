"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.communication import PubkeeperCommunication, \
    PubkeeperCommunicationHandler


class PubkeeperClientCommunication(PubkeeperCommunication,
                                   PubkeeperCommunicationHandler):
    # pragma: no cover
    def start(self, on_message, on_connected=None,
              on_disconnected=None, **kwargs):
        """start

        Called when the client is configuring.  A good place to place any
        callbacks that need to sit on the IOLoop for execution

        Args:
            on_message (callable) - Callback that accepts two arguments,
                                    the received data from the comm module
                                    and the remote address
            on_connected (callable) - Callback that accepts one argument
                                      which will be the address of the remote
                                      connection
            on_disconnected (callbable) - Callback that accepts one argument
                                          which is the address of the remote
                                          you have disconnected from
        """
        self._on_message = on_message
        self._on_connected = on_connected
        self._on_disconnected = on_disconnected

        super().start(**kwargs)

    def close(self):
        """close

        Close the connection to the server, should restart attempts to
        reconnect to the server.
        """
        pass

    def read_messages(self):
        """read_messages
        While the communications is running, and you are connected, loop reading
        for potential new messages
        """
        raise NotImplementedError()
