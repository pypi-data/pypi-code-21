"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.communication import PubkeeperCommunicationHandler


class GatewayCommunicationHandler(PubkeeperCommunicationHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._server_comm = self._handler_args['server_comm_class'](
            config=self._handler_args['server_comm_config']
        )
        self._server_comm.start(on_connected=self.connect,
                                on_message=self.return_message,
                                io_loop=self._ioloop)

    def on_disconnected(self):  # pragma: no cover
        super().on_disconnected()
        if self._server_comm:
            self._server_comm.shutdown()
            self._server_comm = None

    def on_message(self, msg):
        if self._server_comm:
            self._server_comm.write_message(msg)

    def return_message(self, msg):
        self.write_message(msg)
