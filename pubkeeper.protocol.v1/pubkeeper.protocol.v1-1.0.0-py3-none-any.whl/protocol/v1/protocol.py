"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.v1.packet import *  #noqa
from struct import unpack, calcsize
import json
import logging


class PubkeeperProtocol():
    _packet_format = '<HH4x'
    _packet_format_size = calcsize(_packet_format)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('pubkeeper.protocol.v1')
        self.handlers = {
            Packet.ERROR: self.on_error,
        }

    @classmethod
    def unpack(cls, data):
        packet, payload_len = unpack(cls._packet_format,
                                     data[:cls._packet_format_size])
        payload = json.loads(
            unpack('<{}s'.format(payload_len),
                   data[cls._packet_format_size:])[0].decode()
        )

        return (packet, payload_len, payload)

    def _write_message(self, message):
        try:
            if isinstance(message, PubkeeperPacket):
                self.logger.debug("Sending: {0} - {1}".format(
                    message.packet.name, message.payload))
                self.write_message(message.gen_packet())
            else:
                self.logger.info("Trying to send a non packet")
        except:
            self.logger.exception("Could not send")

    def on_message(self, message):
        """Handle Incoming Message

        Will handle incoming messages from WebSocket and send to
        respective handler

        Args
            message (string) - Data received from WebSocket
        """
        try:
            (packet, payload_len, payload) = self.unpack(message)
            self.logger.debug("Received: {0} - {1}".
                              format(Packet(packet).name, payload))
            if Packet(packet) in self.handlers:
                self.handlers[Packet(packet)](**payload)
            else:
                self.logger.warning("There is no handler for: {0}".
                                    format(Packet(packet).name))
        except Exception as e:
            if Packet(packet) is not Packet.ERROR:
                self.logger.error('Action error ({0})'.format(e))
                self.write_message(ErrorPacket(
                    message='Action error ({0})'.format(e)
                ))

    def on_error(self, message):
        """on_error

        Called when a ERROR packet is received

        Args:
            message (string) - Error String
        """
        pass
