"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""


class ZMQServerEncryptionContext(object):
    """ Server Encryption Configuration Context

        This context is provided to a server encryption instance
        when configuring it.
    """
    def __init__(self, zmq_context, allowed_ip_addresses, public_keys_dir,
                 server_secret_cert):
        """ Initializes a server encryption context

        Args:
            zmq_context: zmq context
            allowed_ip_addresses (string): comma separated list of ip addresses
                allowed for communication, leave it empty when no ip address
                address restrictions are in place
            public_keys_dir (string): directory holding public keys certificates
            server_secret_cert (string): server secret certificate file
        """
        self.zmq_context = zmq_context
        self.allowed_ip_addresses = allowed_ip_addresses
        self.public_keys_dir = public_keys_dir
        self.server_secret_cert = server_secret_cert


class ZMQClientEncryptionContext(object):
    """ Client Encryption Configuration Context

        This context is provided to a client encryption instance
        when configuring it.
    """
    def __init__(self, server_public_cert, client_secret_cert):
        """ Initializes a client encryption context

        Args:
            server_public_cert (string): server public certificate file
            client_secret_cert (string): client secret certificate file
        """
        self.server_public_cert = server_public_cert
        self.client_secret_cert = client_secret_cert
