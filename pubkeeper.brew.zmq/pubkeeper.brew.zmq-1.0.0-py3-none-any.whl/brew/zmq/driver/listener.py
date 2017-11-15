"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
import zmq
from zmq.eventloop import zmqstream

from pubkeeper.utils.logging import get_logger
from pubkeeper.brew.zmq.driver.socket_options import ZMQSocketOptions


class InvalidPublisherURL(Exception):
    pass


class ZMQListener(object):
    """ Class to subscribe and receive messages from a publisher url
    """

    _TERMINATION_TIMEOUT = 2

    def __init__(self, publisher_url, handler, ioloop):
        """ Initializes the listener.

        Args:
            publisher_url (string): url to connect to, this url was
                obtained from a queue, such queue might have been created
                by another process.
            handler (callback): method that will receive messages posted
                on given url
            ioloop (IOLoop): loop where stream will run
        """
        self.logger = get_logger(self.__class__.__name__)

        self._publisher_url = publisher_url
        self._handler = handler
        self._subscriber_socket = None

        # event loop for non-blocking sockets
        self._io_loop = ioloop
        self._stream = None

    def connect(self, zmq_context, encryption):
        """ Connects to a url by creating a subscriber socket and connecting
        to url.

        In addition to connecting, this method initiates event gathering.

        Args:
            zmq_context: ZMQ context
            encryption (ZMQClientEncryption): encryption instance
        """
        self._subscriber_socket = self._get_subscriber_socket(zmq_context)
        encryption.encrypt_socket(self._subscriber_socket)

        # connect to address
        try:
            self._subscriber_socket.connect(self._publisher_url)
        except Exception:
            self._subscriber_socket.close()

            msg = "Could not connect to: {0}".format(self._publisher_url)
            self.logger.exception(msg)
            raise InvalidPublisherURL(msg)

        # subscribe to everything coming from queue
        self._subscriber_socket.setsockopt_string(zmq.SUBSCRIBE, '')

        # create stream to gather sockets events
        self._stream = zmqstream.ZMQStream(self._subscriber_socket,
                                           self._io_loop)
        self._stream.on_recv(self._message_handler)

        self.logger.debug("ZMQListener for: {0} connected".format(
            self._publisher_url))

    def close(self):
        """ Closes the listener by terminating io_loop thread and closing the
        socket associated with it.
        """
        if self._stream and not self._stream.closed():
            self._stream.stop_on_recv()
            try:
                self._stream.flush()
                self._stream.close()
            except Exception:  # pragma: no cover
                self.logger.debug("Exception when flushing and closing",
                                  exc_info=True)
        self._stream = None

        if self._subscriber_socket and not self._subscriber_socket.closed:
            # verify that is not open just in case, since when stream
            # is closed this socket gets closed as well
            self._subscriber_socket.close()  # pragma: no cover
        self._subscriber_socket = None

        self.logger.debug("ZMQListener for: {0} is closed".format(
            self._publisher_url))

    @staticmethod
    def _get_subscriber_socket(zmq_context):
        """ Creates a new zmq socket.

        Args:
            zmq_context: ZMQ context

        Returns:
            socket (ZMQ socket instance)
        """
        socket = zmq_context.socket(zmq.SUB)
        # set socket zmq options
        ZMQSocketOptions.set(socket)

        return socket

    def _message_handler(self, msgs):
        try:
            self._handler(self._get_msg_data(msgs))
        except Exception:
            self.logger.exception(
                "Exception caught on user function: '{0}'".
                format(self._handler.__name__))

    @staticmethod
    def _get_msg_data(msgs):
        """ Gets the actual message data

        Message contents depend on how they are sent, i.e. send,
        send_multipart, etc, therefore subscriber would know how to interpret
        message.

        This method deals with messages sent through send, therefore there
        is just one part in the list (the message itself)

        Override this method to accommodate other 'sending-ways'

        Args:
            msgs (list): msgs parts as delivered by stream

        Returns:
            msg data

        """
        return msgs[0]
