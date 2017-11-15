"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from random import random
from socket import socket as raw_socket

from pubkeeper.utils.host import Host

__all__ = ["PortManager", "PortNotAvailable"]


class PortNotAvailable(Exception):
    pass


class InvalidIPAddress(Exception):
    pass


class AvailablePort(object):
    """ Provides functionality to "reserve" an arbitrary port, and
    make it available for use at a later time without allowing
    a call that might come in between to grab it.

    There are circumstances where an available port number is desired to
    be known at an earlier time and its actual use might be delayed,
    this class helps by providing such port and having the port in "use"
    until it is released (closed.)

    """
    def __init__(self, ip_address, min_port=None, max_port=None,
                 timeout=0, connect_interval=0.1):
        """ Grabs an available port and leaves it in use.

        Args:
            ip_address (string): port provider's ip address
            min_port (int): if specified, it is used as the minimum
                port to use when scanning for an available port
            max_port (int): if specified, it is used as the maximum
                port to use when scanning for an available port
        """

        self._timeout = timeout
        self._connect_interval = connect_interval
        if min_port is not None and max_port is not None \
                and max_port > min_port:
            # get a random initial port within given range
            initial_port = min_port + int(random() * (max_port - min_port))
            # scan for a port in first partition
            port = self._scan_port(ip_address, initial_port, max_port)
            if not port:
                # if no port was found, scan in second partition
                port = self._scan_port(ip_address, min_port, initial_port)
            if not port:
                raise PortNotAvailable()
            self._port = port
        else:
            # looking for any available socket in the system
            self._socket = raw_socket()
            self._socket.bind((ip_address, 0))
            # if bind ok, grab port and assume it is good for use
            ip, self._port = self._socket.getsockname()

    def get(self):
        """ Provides the reserved port number

        Returns:
            port (int): Reserved port
        """
        return self._port

    def release(self):
        """ Releases the reserved port number
        """
        self._socket.close()

    def _scan_port(self, ip_address, initial_port, max_port):
        """ Starts a loop ending on the first port that binds

        Args:
            ip_address (string): IP Address to use for binding
            initial_port (int): Starting port to use in the scan
            max_port (int): Ending port to use in the scan

        Returns:
            Found port if found one available otherwise None
        """
        port = initial_port
        # keep track within method whether the ip was verified or not,
        # thus avoiding unneeded ip address checks
        ip_verified = False
        while port <= max_port:
            try:
                self._socket = raw_socket()
                self._socket.bind((ip_address, port))
            except IOError:
                if not ip_verified:
                    if Host.is_valid(ip_address):
                        ip_verified = True
                        # did not fail due to ip address,
                        # let it pick the next port
                    else:
                        # wait for ip address to become available
                        ip_verified = Host.wait_for_ip_address(
                            ip_address, self._timeout,
                            self._connect_interval)
                        if ip_verified:
                            # now ip address is available, retry with same port
                            continue
                        raise InvalidIPAddress("IP address: {0} is invalid".
                                               format(ip_address))

                # since ip address is good at this point, try next port
                port += 1
                continue
            return port


class PortManager(object):
    def configure(self, context):
        self._ip_address = context.get('ip_address', '127.0.0.1')
        self._port_manager_min_port = context.get('port_manager_min_port', 8000)
        self._port_manager_max_port = context.get('port_manager_max_port', 8999)
        self._connect_timeout = context.get('connect_timeout', 0)
        self._connect_interval = context.get('connect_interval', 1)

    def get_port(self):
        available_port = AvailablePort(self._ip_address,
                                       self._port_manager_min_port,
                                       self._port_manager_max_port,
                                       self._connect_timeout,
                                       self._connect_interval)
        port = available_port.get()
        available_port.release()
        return port

    def reserve_port(self):
        available_port = AvailablePort(self._ip_address,
                                       self._port_manager_min_port,
                                       self._port_manager_max_port)
        return available_port

    def release_reserved_port(self, available_port):
        available_port.release()
