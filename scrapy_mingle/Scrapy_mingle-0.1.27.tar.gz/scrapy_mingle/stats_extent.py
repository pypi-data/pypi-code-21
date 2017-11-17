#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Date    : 2017-10-19 10:03:58
# @Author  : xuhaomin
# @Version : python3.6

import redis
import logging
from functools import partial
import json
import time

from twisted.internet import task

from scrapy import signals


logger = logging.getLogger(__name__)


class StatsRecord(object):

    """
    --------------- Statistics extension -----------------
    爬取数据记录拓展，用来记录爬虫运行状态 
    记录数值：
        请求数
        响应数（按响应码）
        错误数（按错误类型）
        生成的item数（按item种类）
        分别统计间隔时间的数值（采集间隔来自settings，用一个数组设置）
    实现机制：
        应用scrapy的信号及拓展
        把数据推送绑定到 engine_started信号 上，设置interval 定期推送采集状态
        把数据计数分别绑定到 request_scheduled，response_received，response_downloaded上 实现运行状态的统计
    数据记录位置：
        redis数据库
        key为  {spidername}:{machinename}:{interval}:{type}
            例如：  1688spider:slaver1:5:requests   表示五分钟生成的请求数
                    1688spider:slaver1:1440:error   表示24小时错误
        值为一个列表（确切说应该是个定长队列），记录了最近20条历史信息，每条历史信息为数值或字典
            请求数 ： [int,int..]
            响应数（按响应码）['{200:int,302:int,...}',..]
            生成的item数（按item种类）[int,int..]
    stats标准：
        请求数 ： 'request/{interval}' int 
        响应数（按响应码）:'response/{interval}' dict
        生成的item数（按item种类）:'item/{interval}' dict
    """

    def __init__(self, crawler):

        self.crawler = crawler
        self.count_interval = crawler.settings.getlist(
            'STATS_RECORD_INTERVAL_SECONDS', [60, 3600, 86400])
        # default 5min, 1hour, daily
        self.record_redis_url = crawler.settings.get(
            'STATS_RECORD_REDIS_URL', 'redis://root@127.0.0.1:6379')
        self.record_redis_params = crawler.settings.get(
            'STATS_RECORD_REDIS_PARAMS', {'db': 0})
        self.machine_name = crawler.settings.get(
            'MACHINE_NAME', 'MASTER')

        self.server = redis.StrictRedis.from_url(
            self.record_redis_url, **self.record_redis_params)
        for interval in self.count_interval:
            self.flush_stats(interval)

        crawler.signals.connect(self._spider_opened,
                                signal=signals.spider_opened)
        crawler.signals.connect(self._request_scheduled,
                                signal=signals.request_scheduled)
        crawler.signals.connect(self._item_scraped,
                                signal=signals.item_scraped)
        crawler.signals.connect(self._response_downloaded,
                                signal=signals.response_downloaded)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler)

    def _spider_opened(self, spider):

        # 初始化的时候，把任务加到tasks列表里，方便退出时停止
        self.tasks = []
        spidername = spider.name
        # 用偏函数初始化任务, _recorder为记录函数
        checker = {}
        for interval in self.count_interval:
            checker[interval] = partial(
                self._record_and_flush, interval, spidername)
            tsk = task.LoopingCall(checker[interval])
            self.tasks.append(tsk)
            tsk.start(interval, now=False)

    def _engine_stopped(self):
        for tsk in self.tasks:
            if tsk.running:
                tsk.stop()

    def _record_and_flush(self, interval, spidername):
        # 1、记录数据到redis（维持redis队列长度不变）
        # 2、重新统计下一组数据
        # 3、左进右出
        t = int(time.time())
        # ---------- request ------------
        redis_key_for_request = '{}:{}:{}:request'.format(
            spidername, self.machine_name, interval)
        request_key = 'request/{interval}'.format(interval=interval)
        request_value = {}
        request_value['time'] = t
        request_value['count'] = self.crawler.stats.get_value(
            request_key, 0)
        self.server.lpush(redis_key_for_request, json.dumps(request_value))

        # ---------- response -----------
        redis_key_for_response = '{}:{}:{}:response'.format(
            spidername, self.machine_name, interval)
        response_key = 'response/{interval}'.format(interval=interval)
        response_value = self.crawler.stats.get_value(
            response_key, {})
        response_value['time'] = t
        self.server.lpush(redis_key_for_response, json.dumps(response_value))

        # ----------- item --------------
        redis_key_for_item = '{}:{}:{}:item'.format(
            spidername, self.machine_name, interval)
        item_key = 'item/{interval}'.format(interval=interval)
        item_value = self.crawler.stats.get_value(
            item_key, {})
        item_value['time'] = t
        self.server.lpush(redis_key_for_item, json.dumps(item_value))

        self.flush_stats(interval)

    def flush_stats(self, interval):
        # 初始化stats记录值
        self.crawler.stats.set_value(
            'request/{interval}'.format(interval=interval), 0)
        self.crawler.stats.set_value(
            'response/{interval}'.format(interval=interval), {})
        self.crawler.stats.set_value(
            'item/{interval}'.format(interval=interval), {})

    def _request_scheduled(self, request, spider):
        for interval in self.count_interval:
            key = 'request/{interval}'.format(interval=interval)
            self.crawler.stats.inc_value(key)

    def _response_downloaded(self, response, spider):
        for interval in self.count_interval:
            key = 'response/{interval}'.format(interval=interval)
            d = self.crawler.stats.get_value(
                key, {})
            response_code = response.status
            d[response_code] = d[response_code] + \
                1 if response_code in d else 1

    def _item_scraped(self, item, spider):
        for interval in self.count_interval:
            key = 'item/{interval}'.format(interval=interval)
            d = self.crawler.stats.get_value(
                key, {})
            item_class = item.__class__.__name__
            d[item_class] = d[item_class] + 1 if item_class in d else 1
