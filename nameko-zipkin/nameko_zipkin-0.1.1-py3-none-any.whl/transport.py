from queue import Queue
from threading import Thread, Condition
from urllib.request import Request, urlopen
from abc import abstractmethod, ABCMeta

from nameko.extensions import SharedExtension

from nameko_zipkin.constants import *

# from kafka import SimpleProducer, SimpleClient


class IHandler(metaclass=ABCMeta):
    def start(self):
        pass

    def stop(self):
        pass

    @abstractmethod
    def handle(self, encoded_span):
        pass


class HttpHandler(IHandler):
    def __init__(self, url):
        self.url = url
        self.queue = Queue()
        self._stop = False
        self.thread = None

    def start(self):
        with self._stop:
            self.thread = Thread(target=self._poll)

    def stop(self):
        self.queue.put(StopIteration)
        self.thread.join()

    def handle(self, encoded_span):
        body = b'\x0c\x00\x00\x00\x01' + encoded_span
        request = Request(self.url, body, {'Content-Type': 'application/x-thrift'}, method='POST')
        urlopen(request)

    def _poll(self):
        while True:
            span = self.queue.get()
            if span == StopIteration:
                break
            self.handle(span)

"""
class KafkaHandler(IHandler):
    def __init__(self, hosts, topic, stop_timeout, producer_params):
        self.hosts = hosts
        self.topic = topic
        self.stop_timeout = stop_timeout
        self.producer_params = producer_params
        self.producer = None

    def start(self):
        client = SimpleClient(self.hosts)
        self.producer = SimpleProducer(client, **self.producer_params)

    def stop(self):
        self.producer.stop(self.stop_timeout)

    def handle(self, encoded_span):
        self.producer.send_messages(self.topic, encoded_span)
"""


class Transport(SharedExtension):
    def __init__(self):
        self._handler = None

    def setup(self):
        config = self.container.config[ZIPKIN_CONFIG_SECTION]
        handler_cls = globals()[config[HANDLER_KEY]]
        handler_params = config[HANDLER_PARAMS_KEY]
        self._handler = handler_cls(**handler_params)

    def start(self):
        self._handler.start()

    def stop(self):
        self._handler.stop()

    def handle(self, encoded_span):
        self._handler.handle(encoded_span)
