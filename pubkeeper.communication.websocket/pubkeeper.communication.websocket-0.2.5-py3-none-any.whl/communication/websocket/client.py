"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from pubkeeper.protocol.packet import PubkeeperPacket
from pubkeeper.communication import PubkeeperClientCommunication
from pubkeeper.communication.state import CommState
from tornado import gen, websocket, httputil, httpclient, ioloop
from tornado.websocket import WebSocketClientConnection
from tornado.concurrent import Future


class WebsocketClientCommunication(PubkeeperClientCommunication):
    default_config = {
        'host': None,
        'port': 9898,
        'ca_chain': None,
        'validate': False,
        'websocket_ping_interval': 10,
        'secure': True,
        'resource': 'ws',
        'headers': True
    }

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)

        self._connection = None
        self._connection_future = Future()
        self._connection_state = CommState.READY

        self._ioloop.spawn_callback(self._check_connection)

        # And setup a periodic check to ensure we remain connected to server
        self._connection_callback = ioloop.PeriodicCallback(
            self._check_connection, 10 * 1000, io_loop=self._ioloop,
        )

    @gen.coroutine
    def _check_connection(self):
        if self._connection_state == CommState.READY:
            self._connection_state = CommState.CONNECTING
            try:
                if self.config['headers']:
                    headers = httputil.HTTPHeaders({
                        'Sec-WebSocket-Protocol': 'pubkeeper.n.io'
                    })
                else:
                    headers = None

                url = '{0}://{1}:{2}/{3}'.format(
                    'wss' if self.config['secure'] else 'ws',
                    self.config['host'], self.config['port'],
                    self.config['resource']
                )

                request = httpclient.HTTPRequest(
                    url=url,
                    headers=headers,
                    ca_certs=self.config['ca_chain']  if self.config['ca_chain'] else None,  # noqa
                    validate_cert=self.config['validate'],
                    allow_ipv6=False
                )

                self.logger.info(
                    "Connecting To Websocket Host: {0}".format(url)
                )

                yield websocket.websocket_connect(
                    request,
                    callback=self._on_connect,
                    ping_interval=self.config['websocket_ping_interval']
                )
            except:
                self.logger.exception("Connection Failure")
                self.close()

    def _on_connect(self, future):
        if future.exception():
            self.logger.warn("Connection Failure: ({})".format(
                future.exception()
            ))
            self.close()
        else:
            self._connection = future.result()
            self._connection_future.set_result(future.result())

            self._connection_callback.stop()
            self._connection_state = CommState.CONNECTED

            if self._on_connected:
                self._on_connected()

            self.read_messages()

    def shutdown(self):
        self._running.clear()
        self.close()

    def close(self):
        self._connection_callback.stop()

        if isinstance(self._connection, WebSocketClientConnection):
            self._connection.close()  # pragma: no cover

        self._connection = None
        self._connection_future = Future()
        self._connection_state = CommState.CLOSED

        if self._running.is_set():
            if self._on_disconnected:
                self._on_disconnected()

            self._connection_state = CommState.READY
            self._ioloop.spawn_callback(self._check_connection)
            self._connection_callback.start()

    def get_connection(self):
        return self._connection_future

    def write_message(self, msg, binary=False):
        if self._running.is_set() and \
                self._connection_state == CommState.CONNECTED:
            if isinstance(msg, PubkeeperPacket):
                self.logger.debug("Sending: {0} - {1}".
                                  format(msg.packet.name, msg.payload))
                self._connection.write_message(msg.gen_packet(), binary=binary)
            else:
                self.logger.debug("Sending: {0}".format(msg))
                self._connection.write_message(msg, binary=binary)

    @gen.coroutine
    def read_messages(self):
        while self._connection_state == CommState.CONNECTED:
            msg = yield self._connection.read_message()

            if msg is None:
                self.close()  # pragma: no cover
            else:
                if self._on_message:
                    try:
                        self._on_message(msg)
                    except:
                        self.logger.exception("Unable to read message")
