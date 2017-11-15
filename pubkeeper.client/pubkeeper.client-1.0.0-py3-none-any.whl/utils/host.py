"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from datetime import datetime, timedelta
from time import sleep
from socket import socket as raw_socket

from pubkeeper.utils.logging import get_logger


class Host(object):
    """ Assists in determining ip address connectivity
    """
    @classmethod
    def is_valid(cls, ip_address):
        """ Determine if ip address is valid

        This method finds out if ip address is valid by trying to
        bind a random port for given ip address.

        Its use is recommended for cases where ports are known to be available,
        otherwise a ping-like method would be recommended.

        Args:
            ip_address: ip address

        Return:
            True if ip address is valid, False otherwise
        """
        _socket = raw_socket()
        try:
            # try to bind to a random port from ip address,
            # if port is available assume that ip address is valid
            _socket.bind((ip_address, 0))
        except:
            _socket.close()
            return False

        _socket.close()
        return True

    @classmethod
    def wait_for_ip_address(cls, ip_address, timeout, check_interval):
        """ Waits for an ip address to become available.

        Args:
            ip_address: ip address
            timeout: how long to wait before giving up
                > 0 -> waits for given time to elapse
                0   -> no wait
                < 0 -> no time limit
            check_interval: amount of time to wait before checking

        Return:
            True if ip address become valid, False otherwise
        """
        my_logger = get_logger('pubkeeper.utils.host')
        my_logger.info("Waiting for IP address: {0} to become available".
                       format(ip_address))
        end_time = datetime.now() + timedelta(seconds=timeout)
        while True:
            if timeout >= 0 and datetime.now() > end_time:
                break
            sleep(check_interval)
            if cls.is_valid(ip_address):
                my_logger.info("IP Address: {0} is now available".
                               format(ip_address))
                return True

        return False
