"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.gateway.handler import GatewayCommunicationHandler


class PubkeeperGateway(object):
    def __init__(self, client, gateway_server):
        self.client = client
        self.gateway_server = gateway_server

    def start(self):
        gw_handler = type(
            '_GWHandler',
            (GatewayCommunicationHandler, self.gateway_server.handler),
            {}
        )
        self.gateway_server.handler = gw_handler

        self.gateway_server.start(
            io_loop=self.client._ioloop,
            handler_args={
                'server_comm_class': self.client.server_comm.__class__,
                'server_comm_config': self.client.server_comm.config
            }
        )

    def shutdown(self):
        self.gateway_server.shutdown()
