from multiprocessing import Queue, Process
import time
from socketIO_client import SocketIO
from ..types import Tick, Bar, MarketEvent, Deal
import logging

log = logging.getLogger('SocketIOReciver')


class SocketIOReciver(Process):

    def __init__(self, url, subs, keep_alive_timeout=30):
        Process.__init__(self)
        self.url = url
        self.queue = Queue()
        self.runing = False
        self.subs = subs
        self.io_client = None
        self.keep_alive_timeout = keep_alive_timeout

    def _on_tick(self, msg):
        t = Tick(msg)
        self.queue.put(('tick', t))

    def _on_bar(self, msg):
        b = Bar(msg)
        self.queue.put(('bar', b))

    def _on_market_event(self, msg):
        sp = msg.split(',')
        e = MarketEvent(sp[0], int(sp[1]), sp[2])
        self.queue.put(('marketEvent', e))

    def _on_deal(self, msg):
        e = Deal(msg)
        self.queue.put(('deal', e))

    def _on_connect(self):
        log.info('reciver connected')
        self.io_client.emit('subscribe', self.subs)

    def _on_disconnect(self):
        log.debug('reciver lost connection')

    def _on_reconnect(self):
        log.debug('reconnected')
        self.io_client.emit('subscribe', self.subs)

    def _on_keepalive(self, t):
        log.debug('keep-alive: %s' % t)

    def run(self):
        self.io_client = SocketIO(
            self.url, wait_for_connection=False)
        self.io_client.on('tick', self._on_tick)
        self.io_client.on('bar', self._on_bar)
        self.io_client.on('deal', self._on_deal)
        self.io_client.on('marketEvent', self._on_bar)
        self.io_client.on('connect', self._on_connect)
        self.io_client.on('disconnect', self._on_disconnect)
        self.io_client.on('reconnect', self._on_reconnect)
        self.io_client.on('keep-alive', self._on_keepalive)
        while True:
            self.io_client.wait(self.keep_alive_timeout)
            self.io_client.emit('keep-alive')

    def generate_events(self):
        if not self.runing:
            self.start()
            self.runing = True
        while True:
            while not self.queue.empty():
                (_type, msg) = self.queue.get()
                yield (_type, msg)
            time.sleep(0.1)
