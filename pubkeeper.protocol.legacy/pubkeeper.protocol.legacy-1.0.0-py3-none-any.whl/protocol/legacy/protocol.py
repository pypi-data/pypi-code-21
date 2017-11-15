"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.legacy.packet import *  #noqa

import json
import logging


class PubkeeperProtocol(object):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger('pubkeeper.protocol.legacy')
        self.handlers = {
            Packet.ERROR: self.on_error,
        }

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
            frame = json.loads(message)
            self.logger.debug("Received: {0} - {1}".
                              format(Packet(frame[0]).name, frame[1]))
            if Packet(frame[0]) in self.handlers:
                self.handlers[Packet(frame[0])](**frame[1])
            else:
                self.logger.warning("There is no handler for: {0} - {1}".
                                    format(Packet(frame[0]).name, frame[1]))
        except Exception as e:
            if Packet(frame[0]) is not Packet.ERROR:
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
