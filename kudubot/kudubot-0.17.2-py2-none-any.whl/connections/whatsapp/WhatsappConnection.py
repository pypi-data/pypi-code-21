u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import with_statement
from __future__ import absolute_import
import ConfigParser
from typing import Dict, List
from yowsup.layers import YowLayerEvent
from yowsup.stacks import YowStackBuilder
from kudubot.users.Contact import Contact
from kudubot.entities.Message import Message
from yowsup.layers.network import YowNetworkLayer
from kudubot.connections.Connection import Connection
from kudubot.exceptions import InvalidConfigException
from kudubot.connections.whatsapp.EchoLayer import EchoLayer
from kudubot.config.GlobalConfigHandler import GlobalConfigHandler
from io import open


class WhatsappConnection(Connection):
    u"""
    Class that implements a kudubot connection for
    the Whatsapp Messaging Service
    """

    def __init__(self, services,
                 config_handler):
        u"""
        Extends the default Connection constructor to create a yowsup stack

        :param services: The services to start
        :param config_handler: The GlobalConfigHandler that determines the
                               location of the configuration files
        """
        super(WhatsappConnection, self).__init__(services, config_handler)

        stack_builder = YowStackBuilder()
        self.yowsup = EchoLayer(self)
        self.stack = \
            stack_builder.pushDefaultLayers(True).push(self.yowsup).build()
        self.stack.setCredentials((self.config[u"number"], self.config[u"pass"]))

    @staticmethod
    def define_identifier():
        u"""
        Defines a unique identifier for the connection

        :return: 'whatsapp'
        """
        return u"whatsapp"

    def define_user_contact(self):
        u"""
        :return: The Whatsapp connection's contact information
        """
        return Contact(-1, u"Kudubot", self.config[u"number"])

    def generate_configuration(self):
        u"""
        Generates a new Configuration file for the Whatsapp Connection

        :return: None
        """
        with open(self.config_file_location, u'w') as config:
            config.write(
                u"[credentials]\nnumber=YourNumberHere\npass=YourPassHere\n")
            self.logger.info(
                u"Wrote new Configuration file at " + self.config_file_location)

    def load_config(self):
        u"""
        Loads the configuration for the Whatsapp Connection
        from the config file

        :return: The parsed configuration,
                 consisting of a dictionary with a number and pass key
        """
        try:

            self.logger.info(u"Parsing config at " + self.config_file_location)

            config = ConfigParser.ConfigParser()
            config.read(self.config_file_location)
            parsed_config = dict(config.items(u"credentials"))

            if parsed_config[u"number"] == u"":
                self.logger.warning(
                    u"Config Parsing Failed. No number supplied.")
                raise InvalidConfigException(
                    u"Invalid Whatsapp Configuration File - "
                    u"Missing number detected")
            elif parsed_config[u"pass"] == u"":
                self.logger.warning(
                    u"Config Parsing Failed. No password supplied.")
                raise InvalidConfigException(
                    u"Invalid Whatsapp Configuration File - "
                    u"Missing password detected")

            self.logger.info(u"Config successfully loaded")

            return parsed_config

        except ConfigParser.NoSectionError:
            self.logger.warning(u"Config Parsing Failed. "
                                u"No credentials section in config file.")
            raise InvalidConfigException(u"Invalid Whatsapp Configuration File "
                                         u"- No credentials section")
        except KeyError, e:
            self.logger.warning(
                u"Config Parsing Failed. No attribute " + unicode(e) + u" found.")
            raise InvalidConfigException(
                u"Invalid Whatsapp Configuration File - No '" + unicode(e) +
                u"' attribute found")

    def send_message(self, message):
        u"""
        Sends a Text message using the Whatsapp Connection

        :param message: The message to send
        :return: None
        """
        self.yowsup.send_text_message(
            message.message_body, message.receiver.address)

    def send_audio_message(self, receiver, audio_file,
                           caption = u""):
        u"""
        Sends an audio message using the Whatsapp Connection

        :param receiver: The receiver of the audio message
        :param audio_file: The audio file to send
        :param caption: An optional caption for the audio message
        :return: None
        """
        self.yowsup.send_audio_message(audio_file, receiver.address, caption)

    def send_video_message(self, receiver, video_file,
                           caption = u""):
        u"""
        Sends a video message using the Whatsapp Connection

        :param receiver: The receiver of the video message
        :param video_file: The video file to send
        :param caption: An optional caption for the video message
        :return: None
        """
        self.yowsup.send_video_message(video_file, receiver.address, caption)

    def send_image_message(self, receiver, image_file,
                           caption = u""):
        u"""
        Sends an image message using the Whatsapp Connection

        :param receiver: The receiver of the image message
        :param image_file: The image file to send
        :param caption: An optional caption for the image message
        :return: None
        """
        self.yowsup.send_image_message(image_file, receiver.address, caption)

    def listen(self):
        u"""
        Starts the Yowsup listener

        :return: None
        """
        self.stack.broadcastEvent(
            YowLayerEvent(YowNetworkLayer.EVENT_STATE_CONNECT)
        )
        self.stack.loop()
