# BOT Motion Module
#
# Ethernet Socket
#
# Author:      Henrik Stroetgen <hstroetgen@synapticon.com> / <support@synapticon.com>
# Date:        2016-11-19
# Location:    Filderstadt, Germany
#
#
#
#       Copyright (c) 2016, Synapticon GmbH
#       All rights reserved.
#
#       Redistribution and use in source and binary forms, with or without
#       modification, are permitted provided that the following conditions are met:
#
#       1. Redistributions of source code must retain the above copyright notice, this
#          list of conditions and the following disclaimer.
#       2. Redistributions in binary form must reproduce the above copyright notice,
#          this list of conditions and the following disclaimer in the documentation
#          and/or other materials provided with the distribution.
#       3. Execution of this software or parts of it exclusively takes place on hardware
#          produced by Synapticon GmbH.
#
#       THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
#       ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
#       WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
#       DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
#       ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#       (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
#       LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#       ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
#       (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
#       SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#       The views and conclusions contained in the software and documentation are those
#       of the authors and should not be interpreted as representing official policies,
#       either expressed or implied, of the Synapticon GmbH.
#

import socket
import netifaces as ni

from ex_thread import *
from config import *
from debug_printing import *

QUEUE_TIMEOUT = 0.1


class ExceptionSocketError(Exception):
    """
    Exception class for socket errors
    """
    pass


class ExceptionInterface(Exception):
    """
    Exception class for interface error
    """
    pass


class EthernetSocket(ExThread):
    """
    Ethernet socket class. Subclasses ExThread
    """

    def __init__(self, id, if_name, address, port, proto, timeout=0.1):
        """
        Initialize Ethernet socket. Sending and receving over ethernet.
        :param id: Object ID
        :type id: uint
        :param if_name: Network interface
        :type if_name: string
        :param address: IP address of axis
        :type address: string
        :param port: TCP/UDP port
        :type port: uint
        :param proto: Network protocol (TCP or UDP)
        :type proto: string
        :param timeout: Socket timeout (Standard 100 ms)
        :type timeout: float
        """

        super(EthernetSocket, self).__init__()
        self.__socket = None
        self.__id = id
        self.__if = if_name
        self.host = self.get_host_ip()
        self.__address = address
        self.__port_master = port

        if proto == 'TCP':
            self.__port_slave = TCP_PORT
            self.__proto = socket.SOCK_STREAM
        elif proto == 'UDP':
            self.__port_slave = UDP_PORT
            self.__proto = socket.SOCK_DGRAM

        self.__printer = DebugPrint(self.__id, 'Socket')
        self.__timeout = timeout
        self.__q_cmd = Queue.Queue()
        self.__q_reply = Queue.Queue()
        self.__alive = threading.Event()
        self.__alive.set()
        self.counter_in = 0
        self.counter_out = 0

    def run_with_exception(self):
        """
        Socket thread. Responsible for receiving data.
        """
        while self.__alive.isSet():
            try:
                data = self.__socket.recvfrom(1024)
                self.__q_reply.put(data)
                if data:
                    self.counter_in += 1
            except socket.timeout:
                continue

        self.__printer.printf('Exit Socket Thread...\n')

    def _open(self):
        """
        Creates an ethernet socket, set timeout and other socket settings.
        :exception: ExceptionSocketError if not possible to create socket.
        """
        # print 'Open Socket...'
        try:
            self.__socket = socket.socket(socket.AF_INET, self.__proto)  # socket.SOCK_DGRAM)
            self.__socket.settimeout(self.__timeout)
            if self.__proto == socket.SOCK_STREAM:
                self.__socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        except socket.error as (value,message):
            raise ExceptionSocketError('Unable to create socket, ' + message)

    def set_broadcast(self):
        """
        Set special broadcast socket. Just necessary for DHCP.
        """
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__socket.settimeout(self.__timeout)
        self.__socket.bind((self.host, self.__port_master))
        self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.start()


    def connect(self):
        """
        Opens socket and connect to node.
        :exception: ExceptionSocketError if unable to connect
        """
        # print 'Connect...'
        self._open()
        try:
            self.__socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.__socket.bind((self.host, 0))# self.__port_master))
            self.__socket.connect((self.__address, self.__port_slave))
        except socket.error as e:
            #print e
            raise ExceptionSocketError('Unable to connect')

        self.start()

    def send(self, data):
        """
        Send data over socket to node.
        :param data: data for node
        :type data: binary string
        """
        sent = self.__socket.send(data)
        self.counter_out += 1

    def sendto(self, data, address):
        """
        Send data over socket to special address
        :param data: date for node
        :type data: binary string
        :param address: IP address of special node
        :type address: string
        """
        sent = self.__socket.sendto(data, address)

    def recv(self):
        """
        Received data from socket thread over queue.
        :return: received data or None
        :rtype: binary string
        """
        data = None
        try:
            data = self.__q_reply.get(True, QUEUE_TIMEOUT)
            self.__q_reply.task_done()
        except Queue.Empty:
            pass

        return data

    def get_host_ip(self):
        """
        Get IP address of network interface.
        :exception: ExceptionInterface if interface is unknown.
        :return: IP address
        :rtype: string
        """
        try:
            ip = ni.ifaddresses(self.__if)[2][0]['addr']
            return ip
        except:
            raise ExceptionInterface('Wrong interface')

    def get_slave_ip(self):
        # TODO still necessary?
        """
        Return address of node.
        :return: IP address
        :rtype: string
        """
        return self.__address

    def close(self):
        """
        Clears alive event and closes ethernet socket
        """
        print "close socket"
        self.__alive.clear()
        self.__socket.close()
