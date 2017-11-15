"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
# Note:
# 1) In win ZMQ_MAX_SOCKETS 1024 raises an error


ZMQSettings = {
    # The linger period determines how long pending messages which have yet to
    # be sent to a peer shall linger in memory after a socket is closed
    'linger': 1000,
    # The high water mark is a hard limit on the maximum number of outstanding
    # messages ØMQ shall queue in memory for any single peer that the specified
    # socket is communicating with
    'hwm_size': 100000,
    # sets the maximum number of sockets allowed on the context
    'max_sockets': 1023,
    # specifies the size of the ØMQ thread pool to handle I/O operations
    'max_io_thread_count': 1,
    # if provided, it will override ip_address
    'ip_interface': None,
    # address used when creating publishing queues
    'ip_address': '127.0.0.1',
    # maximum number of retries when binding a new socket
    'socket_max_retry': 3,
    # minimum port value that a new publisher can be assigned to
    'port_manager_min_port': 9010,
    # maximum port value that a new publisher can be assigned to
    'port_manager_max_port': 9199,
    # encryption settings
    'allowed_ip_addresses': None,
    # used for zmq strongest security model
    # This is a setting that must be set on the publisher instance.
    # Every subscriber's client public key should go in this directory.
    # The public keys for each client should be paired with the client's
    # secret that is set on that host's 'subscriber_client_secret_cert'
    'publisher_public_keys_dir': None,
    # publisher server-like certificates
    # The instance containing publishers must set it's server secret key.
    # All subscriber nodes only need to set the server's public key.
    'publisher_server_public_cert': None,
    'publisher_server_secret_cert': None,
    # subscriber client-like certificates
    # This client's secret key. This will be paired with the public key
    # that should be copied to the publisher instance's public keys folder
    'subscriber_client_secret_cert': None
}
