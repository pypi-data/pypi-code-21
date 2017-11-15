"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.utils.logging import get_logger
from tornado import ioloop, gen, httputil, httpclient
from tornado.websocket import WebSocketClientConnection, websocket_connect
from enum import IntEnum


class CommState(IntEnum):
    READY = 1
    CONNECTING = 2
    CONNECTED = 3
    CLOSED = 4


class WebsocketConnection(object):
    default_config = {
        'host': None,
        'port': 9898,
        'ca_chain': None,
        'validate': False,
        'websocket_ping_interval': 10,
        'secure': True,
        'resource': 'ws',
        'headers': None,
        'state_change_callback': None,
        'connect_timeout': 2
    }

    def __init__(self, config, io_loop=None):
        self.logger = get_logger('pubkeeper.utils.websocket')

        self._config = None
        self._parse_config(config)

        if io_loop is not None:
            self._ioloop = io_loop
        else:
            self._ioloop = ioloop.IOLoop.current()

        self._connection = None
        self._connection_state = CommState.READY
        self._connection_callback = ioloop.PeriodicCallback(
            self._check_connection, 10 * 1000, io_loop=self._ioloop,
        )

    @property
    def server_url(self):
        return '{0}://{1}:{2}/{3}'.format(
            'wss' if self._config['secure'] else 'ws',
            self._config['host'], self._config['port'],
            self._config['resource']
        )

    def _parse_config(self, config):
        self._config = self.default_config.copy()

        non_casting_types = [type(None), str]
        for key in self._config.keys():
            if key in config:
                _type = type(self._config[key])
                if _type in non_casting_types:
                    self._config[key] = config[key]
                else:
                    self._config[key] = _type(config[key])

    def start(self, on_connected=None, on_message=None, on_disconnect=None,
              on_selected_subprotocol=None):
        self._on_connected = on_connected
        self._on_message = on_message
        self._on_disconnect = on_disconnect
        self._on_selected_subprotocol = on_selected_subprotocol

        self._ioloop.spawn_callback(self._check_connection)
        self._connection_callback.start()

    def stop(self, restart=False):
        if isinstance(self._connection, WebSocketClientConnection):
            self._connection.close()

        self._connection = None
        self._connection_state = CommState.CLOSED
        self._connection_callback.stop()

        if self._on_disconnect:
            self._on_disconnect()

        if restart:
            self._connection_state = CommState.READY
            self._connection_callback.start()

    @gen.coroutine
    def _check_connection(self):
        if self._connection_state == CommState.READY:
            self._connection_state = CommState.CONNECTING
            try:
                if self._config['headers']:
                    headers = httputil.HTTPHeaders({
                        'Sec-WebSocket-Protocol': ','.join(
                            self._config['headers']
                        )
                    })
                else:
                    headers = None

                request = httpclient.HTTPRequest(
                    url=self.server_url,
                    headers=headers,
                    ca_certs=self._config['ca_chain'] if self._config['ca_chain'] else None,  # noqa
                    validate_cert=self._config['validate'],
                    request_timeout=self._config['connect_timeout'],
                    allow_ipv6=False
                )

                self.logger.info(
                    "Connecting To Websocket Host: {0}".format(self.server_url)
                )

                connection = yield websocket_connect(
                    request,
                    ping_interval=self._config['websocket_ping_interval'],
                )
                self._connected(connection)
            except Exception as e:
                self.logger.warn("Connection Failure: {} ({})".format(
                    self.server_url, e
                ))
                self.stop(True)

    def _connected(self, connection):
        self._connection = connection
        self._connection_callback.stop()
        self._connection_state = CommState.CONNECTED

        if self._on_selected_subprotocol:
            self._on_selected_subprotocol(
                self._connection.headers.get('Sec-Websocket-Protocol'))

        self.read_messages()

        if self._on_connected:
            self._on_connected(connection)

    @gen.coroutine
    def read_messages(self):
        while self._connection_state == CommState.CONNECTED:
            msg = yield self._connection.read_message()

            if msg is None:
                self.logger.warn(
                    "Disconnected from Websocket Herver: {}".format(
                        self.server_url
                    )
                )
                self.stop(True)
                return
            else:
                if self._on_message:
                    try:
                        self._on_message(msg)
                    except:
                        self.logger.exception("Error reading message")
