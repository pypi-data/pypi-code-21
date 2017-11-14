"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.communication import PubkeeperCommunication


class PubkeeperServerCommunication(PubkeeperCommunication):  # pragma: no cover
    def __init__(self, *args, handler=None):
        super().__init__(*args)
        self.handler = None
        self.connected_handlers = {}

    def start(self, handler_args=None, **kwargs):
        super().start(**kwargs)
        self.handler_args = handler_args
