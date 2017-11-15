"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import zmq

from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.zmq.driver.socket_options import ZMQSocketOptions
from pubkeeper.brew.zmq.driver import ZMQSettings
from pubkeeper.utils.port_manager import PortManager


class ZMQQueue(object):
    """The class ZMQQueue creates and configures a tcp publisher socket for
    sending messages.
    """
    def __init__(self, context=None):
        """ Initializes the queue.

        Args:
            context (PublisherContext): contains queue setup data
        """
        self.logger = get_logger(self.__class__.__name__)

        self._port_manager = PortManager()
        self._port_manager.configure(ZMQSettings)
        self._publisher_socket = None
        self._publisher_url = None
        self._port = context.port if context and hasattr(context, "port") \
            else 0

    def __str__(self):
        return "ZMQQueue, publisher url: {0}". format(self._publisher_url)  # pragma: no cover

    def connect(self, zmq_context, encryption):
        """ Prepares queue to accept connections by creating a publisher
        socket and binding it to an available port.

        Args:
            zmq_context: ZMQ context
            encryption (ZMQServerEncryption): encryption instance
        """
        self._publisher_socket = self._get_publisher_socket(zmq_context)
        encryption.encrypt_socket(self._publisher_socket)
        self._publisher_url = self._bind_socket(self._publisher_socket)

        self.logger.debug("ZMQQueue for: {0} is connected".format(
            self._publisher_url))

    def send(self, message):
        """ Send message to connected subscriber sockets.

        Args:
            message: Message to send, the message must provide
                a buffer interface
        """

        # do not allow to use the same socket to send at the same time from
        # different threads
        if self._publisher_socket:
            self._publisher_socket.send(message)
        else:
            msg = 'ZMQQueue for: {0} is not connected'.format(
                self.publisher_url)
            self.logger.error(msg)
            raise RuntimeError(msg)

    def close(self):
        """ Closes the queue by closing the socket associated with it.
        """
        if self._publisher_socket:
            self._publisher_socket.close()
            self._publisher_socket = None

        self.logger.debug("ZMQQueue for: {0} is closed".format(
            self.publisher_url))

    @property
    def publisher_url(self):
        """ Allows access to url a listener (subscriber socket) needs to
        connect to in order to receive messages from this queue.

        Returns:
            url (string): Publisher url
        """
        return self._publisher_url

    @staticmethod
    def _get_publisher_socket(zmq_context):
        """ Creates a new zmq socket, and sets options on it per
        configuration settings.

        Args:
            zmq_context: ZMQ context

        Returns:
            socket (ZMQ socket instance)
        """
        socket = zmq_context.socket(zmq.PUB)
        # set socket zmq options
        ZMQSocketOptions.set(socket)

        return socket

    def _bind_socket(self, socket):
        """ Cause socket to listen to network port, sockets on the
          other side will use "connect" to get to this socket

        Args:
            socket: Socket to bind

        Returns:
            url (string): publishing url
        """
        # get a random port from pool when not specified
        if not self._port:
            # there is a chance that port might not be fully released/closed
            attempt_with_retry = True
        else:
            attempt_with_retry = False

        # Bind
        if attempt_with_retry:
            self.execute_with_retry(socket)
        else:
            socket.bind('tcp://*:{0}'.format(self._port))

        url = 'tcp://{0}:{1}'.format(ZMQSettings["ip_address"], self._port)
        return url

    def execute_with_retry(self, socket):
        """ Tries to allocates and bind a socket to a port retrying n times

        Args:
            socket: socket to bind
        """
        retry_num = 0
        while True:
            try:
                self._port = self._port_manager.get_port()
                socket.bind('tcp://*:{0}'.format(self._port))
                return
            except Exception:
                self.logger.warning(
                    "Binding socket retry-able execution failed".format(
                        exc_info=True))
                retry_num += 1
                stop_retrying = retry_num > ZMQSettings["socket_max_retry"]
                if stop_retrying:
                    # done retrying, so re-raise the exception
                    self.logger.exception(
                        "Out of retries trying to bind socket.")
                    raise
