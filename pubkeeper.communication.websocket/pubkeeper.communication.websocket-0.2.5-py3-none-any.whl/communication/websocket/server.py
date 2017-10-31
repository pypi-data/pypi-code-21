"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.communication import PubkeeperCommunicationHandler
from pubkeeper.protocol.packet import PubkeeperPacket, ErrorPacket
from tornado.websocket import WebSocketHandler, WebSocketClosedError


class WebsocketServerCommunicationHandler(PubkeeperCommunicationHandler,
                                          WebSocketHandler):
    _clients = []

    @property
    def clients(self):
        return WebsocketServerCommunicationHandler._clients

    def check_origin(self, origin=None):
        return True

    def select_subprotocol(self, subprotocols):
        pass

    def open(self):
        self.logger.info('Client Connected')
        self.clients.append(self)

    def on_close(self, *args, **kwargs):
        self.handle_disconnected_client()
        if self in self.clients:
            self.clients.remove(self)

    def write_message(self, packet, binary=False):
        if not isinstance(packet, PubkeeperPacket):
            packet = ErrorPacket(message='Unknown Message Packet')

        try:
            self.logger.debug("Sending: {0} - {1}".
                              format(packet.packet.name, packet.payload))
            super(PubkeeperCommunicationHandler, self).write_message(
                packet.gen_packet(),
                binary=binary
            )
        except WebSocketClosedError as e:
            self.logger.error("Failed Sending: {} - {} | {}".
                              format(packet.packet.name, packet.payload, e))

    def on_message(self, message, *args, **kwargs):
        try:
            super(PubkeeperCommunicationHandler, self).on_message(
                message, *args, **kwargs
            )
        except WebSocketClosedError:
            self.logger.warn('Lost client, removing from Network')
            self.handle_disconnected_client()

    def handle_disconnected_client(self):
        self.client_disconnected()
        self.logger.info('Client Disconnected')
