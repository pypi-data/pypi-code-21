"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import zmq

from pubkeeper.brew.zmq.driver import ZMQSettings


class ZMQSocketOptions(object):
    """ A class that wraps setting options on a zmq socket

    This class serves as a centralized place which all created zmq sockets
    in the system must use to apply configured settings.
    """

    @staticmethod
    def set(socket):
        """ Set options on a zmq socket

        This method sets configured zmq options on socket

        Args:
            socket: zmq socket
        """

        # The high water mark is a hard limit on the maximum number of
        # outstanding messages ØMQ shall queue in memory for any single
        # peer that the specified socket is communicating with
        socket.setsockopt(zmq.SNDHWM, ZMQSettings["hwm_size"])
        socket.setsockopt(zmq.RCVHWM, ZMQSettings["hwm_size"])

        # The linger period determines how long pending messages
        # which have yet to be sent to a peer shall linger in
        # memory after a socket is closed
        socket.setsockopt(zmq.LINGER, ZMQSettings["linger"])
