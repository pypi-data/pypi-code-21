import redis
from functools import partial
from twisted.internet import task
import json
import time
from scrapy import signals
import logging

logger = logging.getLogger(__name__)


class DownloaderStats(object):

    def __init__(self, crawler, interval, server, machine_name):
        self.stats = crawler.stats
        self.count_interval = interval
        self.server = server
        self.error_dict = {}
        self.machine_name = machine_name

        crawler.signals.connect(self._spider_opened,
                                signal=signals.spider_opened)

        for interval in self.count_interval:
            self.flush_stats(interval)

    @classmethod
    def from_crawler(cls, crawler):
        count_interval = crawler.settings.getlist(
            'STATS_RECORD_INTERVAL_SECONDS', [60, 3600, 86400])
        redis_url = crawler.settings.get(
            'STATS_RECORD_REDIS_URL', 'redis://root@127.0.0.1:6379')
        redis_params = crawler.settings.get(
            'STATS_RECORD_REDIS_PARAMS', {'db': 0})
        server = redis.StrictRedis.from_url(
            url=redis_url, **redis_params)
        machine_name = crawler.settings.get(
            'MACHINE_NAME', 'MASTER')

        return cls(crawler, count_interval, server, machine_name)

    def _spider_opened(self, spider):
        # 初始化的时候，把任务加到tasks列表里，方便退出时停止
        self.tasks = []
        spidername = spider.name
        # 用偏函数初始化任务, _recorder为记录函数
        checker = {}
        for interval in self.count_interval:
            checker[interval] = partial(
                self.record_error, interval, spidername)
            tsk = task.LoopingCall(checker[interval])
            self.tasks.append(tsk)
            tsk.start(interval, now=False)

    def record_error(self, interval, spidername):
        # ----------- record exception -------------
        redis_key_for_error = '{}:{}:{}:error'.format(
            spidername, self.machine_name, interval)

        error_value = self.error_dict[interval]
        error_value['time'] = int(time.time())

        self.server.lpush(redis_key_for_error, json.dumps(error_value))

        self.flush_stats(interval)

    def flush_stats(self, interval):
        # 初始化stats记录值
        self.error_dict[interval] = {'total': 0}

    def process_exception(self, request, exception, spider):
        failure_name = exception.__class__.__name__
        for interval in self.count_interval:
            self.error_dict[interval]['total'] += 1
            if failure_name in self.error_dict[interval]:
                self.error_dict[interval][failure_name] += 1
            else:
                self.error_dict[interval][failure_name] = 1
