#!/usr/bin/env python
# -*- coding: utf-8 -*-
import redis
import rediscluster
from scrapy.exceptions import IgnoreRequest


class ERROR_HANDLE(object):

    def __init__(self, server, dupefilter_key, queue_key, allow_code):
        self.server = server
        self.dupefilter_key = dupefilter_key
        self.queue_key = queue_key
        self.allow_code = allow_code

    @classmethod
    def from_settings(cls, settings):
        dupefilter_key = settings.get('SCHEDULER_DUPEFILTER_KEY')
        queue_key = settings.get('SCHEDULER_QUEUE_KEY')

        allow_code = settings.get('ALLOW_CODE', [])

        USE_CLUSTER = settings.get('USE_CLUSTER')
        if USE_CLUSTER:
            REDIS_NODES = settings.get('REDIS_NODES')
            server = rediscluster.StrictRedisCluster(
                startup_nodes=REDIS_NODES)
        else:
            REDIS_PARAMS = settings.get('REDIS_PARAMS')
            REDIS_URL = settings.get('REDIS_URL')
            server = redis.StrictRedis.from_url(
                url=REDIS_URL, **REDIS_PARAMS)

        return cls(server, dupefilter_key, queue_key, allow_code)

    def process_response(self, request, response, spider):
        if 'good' in response.flag:
            return response
        elif 'retry' in response.flag:
            if response.status in self.allow_code:
                pid = request.meta['pid']
                cid = request.meta.get('category', '')
                ts = request.meta.get('ts', 0)
                self.server.srem(self.dupefilter_key, pid)
                if cid:
                    self.server.lpush(
                        self.queue_key, 'p:{}|{}|{}'.format(pid, ts, cid))
                else:
                    self.server.lpush(
                        self.queue_key, 'p:{}|{}'.format(pid, ts))
            raise IgnoreRequest
        else:
            return response

    def process_exception(self, request, exception, spider):
        pid = request.meta['pid']
        cid = request.meta.get('category', '')
        ts = request.meta.get('ts', 0)
        self.server.srem(self.dupefilter_key, pid)
        if cid:
            self.server.lpush(
                self.queue_key, 'p:{}|{}|{}'.format(pid, ts, cid))
        else:
            self.server.lpush(
                self.queue_key, 'p:{}|{}'.format(pid, ts))
