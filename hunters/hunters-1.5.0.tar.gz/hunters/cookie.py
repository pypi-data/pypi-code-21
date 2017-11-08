# -*- coding:utf-8 -*-
# Created by qinwei on 2017/9/8
import json

from cachetools import LRUCache


class CookieStore(object):
    """爬虫会话保持"""

    def set(self, key, val):
        pass

    def get(self, key):
        pass


class MemoryCookieStore(CookieStore):
    """内存型的Session"""
    _LRU_CACHE = LRUCache(maxsize=100)

    def set(self, key, val):
        self._LRU_CACHE[key] = val

    def get(self, key):
        return self._LRU_CACHE.get(key)


class RedisCookieStore(CookieStore):
    """"""

    def __init__(self, redis):
        """

        :param redis: redis instance
        """
        self.redis = redis

    def get(self, key):
        data = self.redis.get(self._get_key(key))
        if not data:
            return {}
        return json.loads(data)

    def set(self, key, val):
        #: 所有的Cookie都一个小时过期
        self.redis.setex(self._get_key(key), json.dumps(val, ensure_ascii=False), 3600)

    def _get_key(self, key):
        return "s:hunter-cookie:" + key


if __name__ == '__main__':
    cache = MemoryCookieStore()
    for i in range(200):
        cache.set(i, i)
        print(cache.get(i))
    print(len(cache._LRU_CACHE))
