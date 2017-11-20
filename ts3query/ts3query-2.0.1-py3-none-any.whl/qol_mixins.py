#!/usr/bin/env python3

# The MIT License (MIT)
#
# Copyright (c) 2017      Xyoz Netsphere
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Modules
# ------------------------------------------------
import re

# Data
# ------------------------------------------------
__all__ = ["CommonQolMixin", "ClientQueryQolMixin", "ServerQueryQolMixin"]


# Classes
# ------------------------------------------------
class CommonQolMixin:
    """
    Various quality-of-life methods for interaction and data-gathering (context) on universal connections.
    """

    def conn(self):
        """
        Overwrite in Connection to return the connection object.
        :return: current ts3 (universal) connection.
        """
        pass

    def sendcoloredtextmessage(self, *, color: str, msg, targetmode, target):
        """
        Wraps message in color tags before sending.
        .. seealso:: :meth:`~commands.TS3UniversalCommands.sendtextmessage`
        :param color: Hex string or name of color, e.g. #1433b1 or blue.
        :return:
        """
        self.conn().sendtextmessage(msg='[color={color}]{msg}[/color]'.format(color=color, msg=msg),
                                    targetmode=targetmode, target=target)


class ClientQueryQolMixin(CommonQolMixin):
    """
    Various quality-of-life methods for interaction and data-gathering (context) on ClientQuery connections.
    """

    def is_username_in_channel(self, *, username_regex: str) -> bool:
        """
        Checks if user(s) matching a provided regex are in the same channel as the actor.
        :param username_regex: Regex for matching with usernames in channel.
        :type: str
        :return: True if matching username is found, False otherwise.
        :type: bool
        """
        clientlist = self.conn().clientlist()
        whoami = self.conn().whoami()

        for client in clientlist.parsed:
            if re.match(username_regex, client['client_nickname']) and client['cid'] == whoami[0]['cid']:
                return True

        return False

    def clientmultiplenotifyregister(self, *, notifies: list, schandlerid: int):
        """
        See :meth:`~commands.TS3ClientCommands.clientnotifyregister` for more information.
        :param notifies: List of event-values which the actor should be notified about.
        :type: list
        """
        for notify in notifies:
            self.conn().clientnotifyregister(event=notify, schandlerid=schandlerid)

    def clientmultiplenotifyunregister(self, *, notifies: list, schandlerid: int):
        """
        See :meth:`~commands.TS3ClientCommands.clientnotifyunregister` for more information.
        :param notifies: List of event-values which the actor should not be notified about.
        :type: list
        """
        for notify in notifies:
            self.conn().clientnotifyunregister(event=notify, schandlerid=schandlerid)

    def clientallnotifyregister(self, *, schandlerid: int):
        """
        Subscribes to all notify events.
        :param schandlerid: virtual server id which should be subscribed on (0 for every)
        :type: int
        """
        self.conn().clientnotifyregister(event='all', schandlerid=schandlerid)

    def clientallnotifyunregister(self, *, schandlerid: int):
        """
        Unsubscribes from all notify events.
        :param schandlerid: virtual server id which should be unsubscribed on (0 for every)
        :type: int
        """
        self.conn().clientnotifyunregister(event='all', schandlerid=schandlerid)

    def cid_from_clid(self, clid):
        """
        Returns the channel id in which the client with the clid is currently in.
        :param clid: client id
        :return: channel id or None
        """
        clientlist = self.conn().clientlist()
        for client in clientlist:
            if str(client['clid']) == str(clid):
                return client['cid']


class ServerQueryQolMixin(CommonQolMixin):
    """
    Various quality-of-life methods for interaction and data-gathering (context) on ServerQuery connections.
    """
    pass
