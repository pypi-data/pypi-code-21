"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from zmq.auth import load_certificate
from zmq.auth.thread import ThreadAuthenticator

from pubkeeper.utils.logging import get_logger


class ZMQServerEncryption(object):
    """ Supports server-like encryption communications

    If encryption arguments are not provided (they are kept as None), this class
    currently does not raise exceptions thus allowing for backwards
    compatibility (or no encryption) without having to modify clients
    of this class.

    To generate certificates use python script generate_certificates.py
    """

    def __init__(self):
        """ Initializes an instance of the server encryption class
        """
        super().__init__()
        self.logger = get_logger(self.__class__.__name__)

        self._zmq_context = None
        self._thread_auth = None
        self._public_keys_dir = None
        self._allowed_ip_addresses = None
        self._server_public = None
        self._server_secret = None

    def configure(self, context):
        """ Configures a server encryption instance

        Note that keys are set only when certificates are provided.
        """
        self._zmq_context = context.zmq_context
        self._public_keys_dir = context.public_keys_dir
        self._allowed_ip_addresses = context.allowed_ip_addresses
        if context.server_secret_cert:
            self._server_public, self._server_secret = \
                load_certificate(context.server_secret_cert)

    def start(self):
        """ Starts encryption for a given context
        """
        if self._public_keys_dir:
            # Start an authenticator for this context.
            self._thread_auth = ThreadAuthenticator(self._zmq_context)
            self._thread_auth.start()
            if self._allowed_ip_addresses:
                # pass allowed ips as *args trimming spaces in between
                self._thread_auth.allow(
                    *[ip.strip()
                      for ip in self._allowed_ip_addresses.split(',')])

            # Tell the authenticator how to handle CURVE requests
            self._thread_auth.configure_curve(
                location=self._public_keys_dir)
            self.logger.info("zmq communications are encrypted")
        else:
            self.logger.info("Public keys directory is not set, "
                             "zmq communications are not encrypted")

    def stop(self):
        """ Stops encryption thread attached to context
        """
        if self._thread_auth:
            self._thread_auth.stop()

    def encrypt_socket(self, socket):
        """ Sets up a server socket for encryption

        Args:
            socket (zmq socket): socket to encrypt
        """
        if self._server_secret and self._server_public:
            socket.curve_secretkey = self._server_secret
            socket.curve_publickey = self._server_public
            # must come before bind
            socket.curve_server = True


class ZMQClientEncryption(object):
    """ Supports client-like encryption communications

    If encryption arguments are not provided (they are kept as None), this class
    currently does not raise exceptions thus allowing for backwards
    compatibility (or no encryption) without having to modify clients
    of this class.

    To generate certificates use python script generate_certificates.py
    """

    def __init__(self):
        """ Initializes an instance of the client encryption class
        """
        super().__init__()
        self._server_public = None
        self._client_public = None
        self._client_secret = None

    def configure(self, context):
        """ Configures a client encryption instance

        Note that keys are set only when certificates are provided.
        """
        if context.client_secret_cert:
            self._client_public, self._client_secret = \
                load_certificate(context.client_secret_cert)
        if context.server_public_cert:
            self._server_public, _ = \
                load_certificate(context.server_public_cert)

    def encrypt_socket(self, socket):
        """ Sets up a client socket for encryption

        Args:
            socket (zmq socket): socket to encrypt
        """
        if self._client_secret and self._client_public and self._server_public:
            socket.curve_secretkey = self._client_secret
            socket.curve_publickey = self._client_public
            socket.curve_serverkey = self._server_public
