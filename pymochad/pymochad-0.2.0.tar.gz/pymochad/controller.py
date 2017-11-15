# Copyright 2016 Matthew Treinish
#
# This file is part of pymochad
#
# pymochad is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# pymochad is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with pymochad. If not, see <http://www.gnu.org/licenses/>.

import logging
import socket
import time

import six

from pymochad import exceptions

LOG = logging.getLogger(__name__)


class PyMochad(object):
    """PyMochad controller class

    This class is used to create a PyMochad controller object that is used to
    send commands to a running PyMochad daemon.

    :param str server: The host to connect to the pymochad socket on, it
                       defaults to localhost
    :param int port: The port to use for remote connections. If one is not
                     provided it will just use the default port of 1099.
    """
    def __init__(self, server=None, port=1099):
        super(PyMochad, self).__init__()
        self.port = port
        self.server = server or 'localhost'
        self._connect()

    def _connect(self):
        for addr in socket.getaddrinfo(self.server, self.port):
            af, socktype, proto, cannonname, sa = addr
            try:
                self.socket = socket.socket(af, socktype, proto)
                self.socket.connect(sa)
            except Exception:
                continue
            break
        else:
            raise exceptions.ConfigurationError(
                "Unable to connect to server %s" % self.server)
        self.socket.setblocking(0)

    def reconnect(self):
        """Reconnect when mochad server is restarted/lost connection."""
        if self.socket:
            self.socket.close()
        self._connect()

    def send_cmd(self, cmd):
        """Send a raw command to mochad.

        :param str cmd: The command to send to mochad
        """
        self.socket.sendall(six.binary_type(cmd.encode('utf8')))

    def read_data(self):
        """Read data from mochad

        :return data: The data returned over the mochad socket
        :rtype: str
        """

        total_data = []
        while True:
            try:
                data = self.socket.recv(4096)
                if not data:
                    break
                total_data.append(six.text_type(data.decode('utf8')))
                line_break = six.binary_type('\n'.encode('utf8'))
                if data.endswith(line_break):
                    break
            except socket.error as e:
                if e.errno == socket.errno.EWOULDBLOCK:
                    time.sleep(1)
                    continue
                else:
                    raise
        return ''.join(total_data)

    def status(self):
        """Send a show device status command.

        :return status: The status of device including RF security devices
        :rtype: str
        """
        self.send_cmd('st\n')
        return self.read_data()
