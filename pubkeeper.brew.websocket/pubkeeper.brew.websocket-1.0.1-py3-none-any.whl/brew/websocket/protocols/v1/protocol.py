from pubkeeper.protocol.v1.frame import Frame
from pubkeeper.brew.websocket.protocols.v1.packet import \
    WebSocketPacket, WebSocketPacketType
from pubkeeper.utils.logging import get_logger


class Protocol(object):
    def __init__(self):
        self.logger = get_logger("Brew v1 protocol")

    def on_connected(self, connection, topic):
        self._send_message(connection, WebSocketPacketType.join, topic)

    def on_disconnected(self, connection, topic):
        self._send_message(connection, WebSocketPacketType.leave, topic)

    def brew(self, connection, brewer_id, topic, data):
        self._send_message(connection,
                           WebSocketPacketType.publish, topic,
                           data)

    @staticmethod
    def unpackage_data(data):
        _, brewer_id, _ = Frame.unpack(data)
        return brewer_id, data

    def _send_message(self, connection, packet, topic, data=None):
        connection.write_message(
            WebSocketPacket.pack(packet, topic, data),
            binary=True
        )
