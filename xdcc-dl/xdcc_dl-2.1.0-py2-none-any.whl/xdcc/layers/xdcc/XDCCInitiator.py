u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
import os
import shlex
import irc.client
from typing import List
# noinspection PyPep8Naming
from xdcc_dl.logging.LoggingTypes import LoggingTypes as LOG
from xdcc_dl.xdcc.layers.xdcc.MessageSender import MessageSender
from io import open


class IncorrectFileSentException(Exception):
    u"""
    Gets raised whenever the bot sends the incorrect,
    or at least not-predicted file
    """
    pass


class NoValidWhoisQueryException(Exception):
    u"""
    Gets raised when a bot is encountered that requires the user to join
    a specific channel, but does not provide the identity
    of that channel via whois
    """


# noinspection PyUnusedLocal
class XDCCInitiator(MessageSender):
    u"""
    Initiates the XDCC Connection.
    Layer 4 of the XDCC Bot
    """

    def on_ctcp(self, connection,
                event):
        u"""
        Client-to-Client Connection which initiates the XDCC handshake

        :param connection: the IRC Connection
        :param event:      the IRC Event
        :return:           None
        """
        super(XDCCInitiator, self).on_ctcp(connection, event)

        if event.arguments[0] != u"DCC":
            return

        payload = shlex.split(event.arguments[1])

        if payload[0] == u"SEND":
            self.dcc_send_handler(payload, connection)
        elif payload[0] == u"ACCEPT":
            self.dcc_accept_handler(payload, connection)
        else:  # pragma: no cover
            return

    def dcc_send_handler(self, ctcp_arguments,
                         connection):
        u"""
        Handles incoming CTCP DCC SENDs.
        Initiates a download or RESUME request.

        :param ctcp_arguments: The CTCP Arguments
        :param connection: The connection to use for DCC connections
        :raises: AlreadyDownloaded, if the file was already downloaded
        :return: None
        """
        self.logger.log(u"Handling DCC SEND Handshake", LOG.DCC_SEND_HANDSHAKE)

        filename = ctcp_arguments[1]
        if not self.current_pack.is_filename_valid(filename):
            self.logger.log(u"Incorrect file sent", LOG.INCORRECT_FILE)
            raise IncorrectFileSentException()

        self.peer_address = irc.client.ip_numstr_to_quad(ctcp_arguments[2])
        self.peer_port = int(ctcp_arguments[3])
        self.filesize = int(ctcp_arguments[4])

        self.progress.set_single_progress_total(int(self.filesize))
        self.current_pack.set_filename(filename)

        if os.path.exists(self.current_pack.get_filepath()) and \
                not self.dcc_resume_requested:

            position = os.path.getsize(self.current_pack.get_filepath())

            if position >= self.filesize:

                self.logger.log(u"File already completely downloaded. Aborting",
                                LOG.DOWNLOAD_WAS_DONE)
                self.already_downloaded = True
                self.dcc_connection = self.dcc_connect(
                    self.peer_address, self.peer_port, u"raw"
                )

            else:

                self.logger.log(u"Requesting DCC RESUME",
                                LOG.DCC_RESUME_REQUEST)
                self.progress.set_single_progress(position)

                # Let bot know that resume was attempted
                self.dcc_resume_requested = True
                resume_parameter = u"\"" + filename + u"\" " + \
                                   unicode(self.peer_port) + u" " + unicode(position)

                # -> on_ctcp -> dcc_accept_handler
                # (Or dcc_send_handler if resume fails)
                connection.ctcp(u"DCC RESUME", self.current_pack.get_bot(),
                                resume_parameter)

        else:

            if self.dcc_resume_requested:
                self.logger.log(u"DCC Resume Failed. Starting from scratch.",
                                LOG.DCC_RESUME_FAILED)
                os.remove(self.current_pack.get_filepath())
                self.progress.set_single_progress(0)

            self.logger.log(u"Starting Download of " + filename,
                            LOG.DOWNLOAD_START)

            self.file = open(self.current_pack.get_filepath(), u"wb")
            self.dcc_connection = self.dcc_connect(
                self.peer_address, self.peer_port, u"raw"
            )  # -> on_dccmsg
            self.download_started = True

    def dcc_accept_handler(self, ctcp_arguments,
                           connection):
        u"""
        Handles DCC ACCEPT messages. Resumes a download.

        :param ctcp_arguments: The CTCP arguments
        :param connection:     The connection to use for DCC connections
        :return:               None
        """
        self.logger.log(u"DCC RESUME request successful",
                        LOG.DCC_RESUME_SUCCESS)
        self.logger.log(
            u"Resuming Download of " + self.current_pack.get_filepath(),
            LOG.DOWNLOAD_RESUME
        )

        self.file = open(self.current_pack.get_filepath(), u"ab")
        self.dcc_connection = self.dcc_connect(
            self.peer_address, self.peer_port, u"raw")  # -> on_dccmsg
        self.download_started = True

    def on_privnotice(self, connection,
                      event):
        u"""
        Checks if a private notice is sent by the sending bot that a pack was
        already requested.
        If that is the case, another attempt will be made on the next ping.
        Also checks for channel-based XDCC denies

        :param connection: the IRC connection
        :param event: the IRC event
        :raises: NoValidWhoisQuery, if the bot told us that no
                 correct channel was joined
        :return: None
        """
        try:
            if u"You already requested that pack" in event.arguments[0]:
                self.logger.log(
                    u"Pack already requested, waiting for next Ping",
                    LOG.ALREADY_REQUESTED
                )
                self.already_requested = True
            elif u"You will have to re-send that," \
                 u"to the bot that transferred the file." in event.arguments[0]:
                connection.privmsg(
                    self.current_pack.get_bot(),
                    self.current_pack.get_request_message()
                )
            elif u"** XDCC SEND denied, you must be on a known channel" \
                 u"to request a pack" in event.arguments[0]:
                raise NoValidWhoisQueryException()
            else:
                super(XDCCInitiator, self).on_privnotice(connection, event)
        except IndexError:
            pass

    def on_ping(self, connection,
                event):
        u"""
        Retries a download on a ping signal
        :param connection:
        :param event:
        :return:
        """
        super(XDCCInitiator, self).on_ping(connection, event)
        if self.already_requested:
            log_message = \
                u"Resending XDCC Request to " + self.current_pack.get_bot()
            log_message += \
                u" for pack " + unicode(self.current_pack.get_packnumber())
            self.logger.log(log_message, LOG.MESSAGE_RETRY)

            self.already_requested = False
            connection.privmsg(
                self.current_pack.get_bot(),
                self.current_pack.get_request_message()
            )  # -> on_ctcp
