import pprint
from collections import defaultdict
from typing import TypeVar

from scrapy.crawler import Crawler
from scrapy.http import Request
from scrapy.spiders import Spider
from scrapy.utils.misc import load_object
from twisted.internet.defer import inlineCallbacks

from ..settings.default_settings import SIGNALS
from ..settings.default_settings import RECYCLE_REQUEST

Obj = TypeVar('Obj', str, object)

pp = pprint.PrettyPrinter(indent=4)


class Validation(object):
    def __init__(self, *, exception: Obj, signal: Obj = None,
                 signal_deferred: Obj = None, limit: int = 1):
        self.exception = load_object(exception)

        if signal:
            self.signal = load_object(signal)
        else:
            self.signal = None

        if signal_deferred:
            self.signal_deferred = load_object(signal_deferred)
        else:
            self.signal_deferred = None

        self.limit = limit


class ProxyValidation(object):
    def __init__(self, crawler: Crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.signals = crawler.signals

        self.abused_records = defaultdict(dict)
        self.signals = defaultdict(dict)

        for validation in self.settings.get(SIGNALS):
            if validation.signal:
                self.signals[validation.exception].setdefault(
                    'signal', {}
                ).update({validation.signal: validation.limit})
            if validation.signal_deferred:
                self.signals[validation.exception].setdefault(
                    'signal_deferred', {}
                ).update({validation.signal_deferred: validation.limit})

        if self.settings.get(RECYCLE_REQUEST):
            self.recycle_request = load_object(
                self.settings.get(RECYCLE_REQUEST))
        else:
            self.recycle_request = load_object(
                'scrapy_proxy_validation.utils.recycle_request.recycle_request'
            )

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        o = cls(crawler)
        return o

    @inlineCallbacks
    def process_exception(self, request: Request, exception: Exception,
                          spider: Spider):
        if exception in self.signals:
            proxy = request.meta['proxy']

            if exception not in self.abused_records[proxy]:
                self.abused_records[proxy][exception] = 0
            self.abused_records[proxy][exception] += 1

            signals = filter(
                lambda x: self.abused_records[proxy][exception] == x[1],
                self.signals[exception].setdefault('signal', {}).items())

            for signal in signals:
                _ = self.crawler.signals.send_catch_log(signal)

            signals_deferred = filter(
                lambda x: self.abused_records[proxy][exception] == x[1],
                self.signals[exception].setdefault('signal_deferred',
                                                   {}).items())

            for signal_deferred in signals_deferred:
                _ = yield self.crawler.signals.send_catch_log_deferred(
                    signal_deferred)

            return self.recycle_request(request)
