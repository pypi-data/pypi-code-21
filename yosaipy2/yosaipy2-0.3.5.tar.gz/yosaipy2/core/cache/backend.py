#!/usr/bin/env python
# -*- coding: utf-8 -*-
from dogpile.cache.backends.redis import RedisBackend
from dogpile.cache.api import NO_VALUE
from dogpile.cache.region import register_backend

__all__ = 'CustomRedisBackend',

register_backend('yosaipy2.cache.redis', 'yosaipy2.core.cache.backend', 'CustomRedisBackend')


class CustomRedisBackend(RedisBackend):
    def __init__(self, arguments):
        super(CustomRedisBackend, self).__init__(arguments)

    def get(self, key):
        value = self.client.get(key)
        if value is None:
            return NO_VALUE
        return value

    def get_multi(self, keys):
        if not keys:
            return []
        values = self.client.mget(keys)
        return [v if v is not None else NO_VALUE
                for v in values]

    def set(self, key, value):
        if self.redis_expiration_time:
            self.client.setex(key, self.redis_expiration_time, value)
        else:
            self.client.set(key, value)

    def set_multi(self, mapping):
        mapping = dict((k, v) for k, v in mapping.items())

        if not self.redis_expiration_time:
            self.client.mset(mapping)
        else:
            pipe = self.client.pipeline()
            for key, value in mapping.items():
                pipe.setex(key, self.redis_expiration_time, value)
            pipe.execute()
