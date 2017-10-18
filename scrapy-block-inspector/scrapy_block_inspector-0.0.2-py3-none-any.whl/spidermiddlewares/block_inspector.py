import logging

from scrapy.utils.misc import load_object
from twisted.internet import defer

from ..exceptions import BlockException

logger = logging.getLogger(__name__)


class BlockInspector(object):
    def __init__(self, crawler):
        self.crawler = crawler
        self.settings = crawler.settings
        self.signals = crawler.signals
        self.stats = crawler.stats

        self.inspect_block = load_object(
            self.settings.get('BLOCK_INSPECTOR'))
        if self.settings.get('RECYCLE_BLOCK_REQUEST'):
            self.recycle_block_request = load_object(
                self.settings.get('RECYCLE_BLOCK_REQUEST'))
        else:
            self.recycle_block_request = lambda x: x
        if self.settings.get('BLOCK_SIGNALS'):
            self.block_signals = list(map(
                lambda x: load_object(x),
                self.settings.get('BLOCK_SIGNALS')))
        else:
            self.block_signals = []
        if self.settings.get('BLOCK_SIGNALS_DEFERRED'):
            self.block_signals_deferred = list(map(
                lambda x: load_object(x),
                self.settings.get('BLOCK_SIGNALS_DEFERRED')))
        else:
            self.block_signals_deferred = []

    @classmethod
    def from_crawler(cls, crawler):
        obj = cls(crawler)
        return obj

    def process_spider_input(self, response, spider):
        if self.inspect_block(response):
            self.stats.inc_value('block_inspector/block', spider=spider)
            raise BlockException(response)

    @defer.inlineCallbacks
    def process_spider_exception(self, response, exception, spider):
        if isinstance(exception, BlockException):
            result = []
            for signal in self.block_signals:
                result.append((
                    signal, self.signals.send_catch_log(
                        signal, spider=spider, response=response,
                        exception=exception)))
            for signal_deferred in self.block_signals_deferred:
                _ = yield self.signals.send_catch_log_deferred(
                    signal_deferred, spider=spider, response=response,
                    exception=exception)
                result.append((signal_deferred, _))

            r = response.request.replace(dont_filter=True)

            # for compatible with python 2.7 and 3.5
            defer.returnValue([self.recycle_block_request(r)])
