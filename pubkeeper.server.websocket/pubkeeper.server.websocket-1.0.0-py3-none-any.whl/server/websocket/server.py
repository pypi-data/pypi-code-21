"""
Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from tornado import web, websocket, httpserver, ioloop, gen, log
from pubkeeper.server.websocket.pool import ConnectionPool
from pubkeeper.server.websocket.packet import WebSocketPacket
import logging
try:
    from signal import signal, SIGINFO
    has_signal = True
except:  # pragma no cover
    from signal import signal, SIGUSR1
    has_signal = False

(JOIN, LEAVE, PUBLISH) = (0, 1, 2)


class ConnectionHandler(websocket.WebSocketHandler):
    pools = {}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._logger = \
            logging.getLogger('pubkeeper.server.websocket.ConnectionHandler')
        self._in_pools = []
        self._message_handlers = {
            JOIN: self._on_join,
            LEAVE: self._on_leave,
            PUBLISH: self._on_publish
        }

    def check_origin(self, origin):  # pragma: no cover
        return True

    def on_close(self):
        for pool in self._in_pools:
            pool.del_socket(self)

    @gen.coroutine
    def on_message(self, message):
        (_type, hashed_topic, data) = WebSocketPacket.unpack(message)

        if _type in self._message_handlers:
            self._message_handlers[_type](hashed_topic, data)
        else:  # pragma no cover
            self._logger.info("Message: '{}' unhandled".format(message))

    def select_subprotocol(self, subprotocols):
        self._logger.info('selecting subprotocol from: {} '.
                          format(subprotocols))
        if len(subprotocols) > 0:
            for subprotocol in subprotocols:
                if '1.0' in subprotocol:
                    self._logger.info(
                        'selected subprotocol: {} '.format(subprotocol))
                    return subprotocol

    @classmethod
    def _get_pool(cls, topic):
        if topic not in cls.pools:
            cls.pools[topic] = ConnectionPool()

        return cls.pools[topic]

    @classmethod
    def _del_pool(cls, topic):
        if topic in cls.pools:
            del(cls.pools[topic])

    def _on_join(self, topic, *args):
        pool = self._get_pool(topic)
        pool.add_socket(self)
        self._in_pools.append(pool)
        self._logger.info("Client {} Joined {}".format(self, topic))

    def _on_leave(self, topic, *args):
        pool = self._get_pool(topic)
        pool.del_socket(self)
        if pool in self._in_pools:
            self._in_pools.remove(pool)

        self._logger.info("Client {} Left {}".format(self, topic))

    def _on_publish(self, topic, data):
        pool = self._get_pool(topic)
        pool.publish(data, ignore=self)


def start_server():  # pragma no cover
    app = web.Application([
        (r"/", ConnectionHandler),
    ], websocket_ping_interval=10)

    http_server = httpserver.HTTPServer(app)
    http_server.listen(8000)

    def print_network(self, *args, **kwargs):
        print("{} pools connected".format(len(ConnectionHandler.pools)))
        for topic, pool in ConnectionHandler.pools.items():
            print("Topic: {}".format(topic))
            for conn in pool._connections:
                print("Has {}".format(conn))

    if has_signal:
        signal(SIGINFO, print_network)
    else:
        signal(SIGUSR1, print_network)

    try:
        logging.getLogger('pubkeeper.server.websocket').info(
            "Websocket Server Started")
        ioloop.IOLoop.current().start()
        ioloop.IOLoop.current().close()
    except KeyboardInterrupt:
        stop_server()


def stop_server():  # pragma no cover
    ioloop.IOLoop.current().stop()
    logging.getLogger('pubkeeper.server.websocket').info(
        "Websocket Server Stopped")


if __name__ == "__main__":  # pragma no cover
    log.enable_pretty_logging()
    logging.getLogger().setLevel(logging.DEBUG)
    start_server()
