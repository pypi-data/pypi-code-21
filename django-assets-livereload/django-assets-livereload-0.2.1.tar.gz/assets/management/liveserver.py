import gevent.lock
import gevent.monkey
import gevent.pywsgi
import gevent.queue
gevent.monkey.patch_all(thread=False)

from geventwebsocket import WebSocketError
from geventwebsocket.handler import WebSocketHandler

import json
import logging
import time

from . import bottle
from .utils import MessageBroker, IP_ANY

logger = logging.getLogger(__name__)

LIVE_PORT = 35729

class LiveServer:

    def _websocket_handler(self):
        logger.info("Registering client")
        q = self._broker.sub()
        try:
            wsock = bottle.request.environ.get('wsgi.websocket')
            while True:
                message = q.get()
                wsock.send(json.dumps(message))
        except WebSocketError:
            pass
        finally:
            self._broker.unsub(q)

    def __init__(self, ip=IP_ANY, port=LIVE_PORT):
        self._broker = MessageBroker()
        self._app = bottle.Bottle()
        self._ip = ip
        self._port = port
        self._app.route('/')(self._websocket_handler)

    def serve_forever(self):
        logger.info("Starting livereload server on {ip}:{port}".format(ip=self._ip, port=self._port))
        self._server = gevent.pywsgi.WSGIServer((self._ip, self._port), self._app, handler_class=WebSocketHandler)
        self._server.serve_forever()

    def reload(self, path=None):
        self._broker.pub({'command': 'reload', 'path': path})

    def status(self, status):
        self._broker.pub({'command': 'status', 'status': status})

    @property
    def url(self):
        return 'ws://{ip}:{port}/'.format(ip=self._ip,port=self._port)




