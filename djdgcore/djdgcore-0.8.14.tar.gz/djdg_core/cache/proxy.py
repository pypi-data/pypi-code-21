#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/29
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.cache.redis_client import cache
from djdg_core.exceptions import TimeOutError
from djdg_core.cache.redlock import Redlock
import time


REDLOCK = Redlock([cache])


class CacheProxy(object):
    """
    缓存代理
    """
    FORMAT = None
    LOCK_PREFIX = 'lock'
    LOCK_EXPIRE = 300
    TIMESTAMP_RATE = 1
    KEY_EXPIRE = None
    WAIT_INTERVAL = 1

    def __init__(self, engine=None, redlock=None, **kwargs):
        if not engine:
            engine = cache
        if not redlock:
            redlock = REDLOCK
        self.logger = kwargs.pop('logger', None)
        self._engine = engine
        self._kwargs = kwargs
        self._key = None
        self._lock_key = None
        self._redlock = redlock
        self._lock = None

    def __getattr__(self, item):
        if item.startswith('hook_'):
            item = item[5:]

            def wrapper(*args, **kwargs):
                return self.hook(item, *args, **kwargs)
            return wrapper
        return getattr(self._engine, item)

    def hook(self, func, *args, **kwargs):
        """
        统一通过管道方式执行命令
        :param func:
        :param args:
        :param kwargs:
        :return:
        """
        expire = kwargs.pop('ex pire', None)
        pipe = self._engine.pipeline()
        call_func = getattr(pipe, func)
        pipe = call_func(self.key, *args, **kwargs)
        if expire and self.KEY_EXPIRE:
            pipe = pipe.expire(self.key, self.KEY_EXPIRE)
        r = pipe.execute()
        return r[0]

    @property
    def formatter(self):
        fmts = []
        for s in self.__class__.__mro__:
            fmt = getattr(s, 'FORMAT', None)
            if fmt:
                fmts.append(fmt)
        fmts.reverse()
        return ':'.join(fmts)

    @property
    def key(self):
        if not self._key:
            self._key = self.formatter.format(**self._kwargs)
        return self._key

    @property
    def lock_key(self):
        if not self._lock_key:
            self._lock_key = ':'.join([self.key, self.LOCK_PREFIX])
        return self._lock_key

    def __enter__(self):
        self.acquire()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    def acquire(self):
        start = time.time()
        while True:
            nt = time.time()
            lock = self._redlock.lock(self.lock_key, self.LOCK_EXPIRE * 1000)
            if lock:
                self._lock = lock
                break
            # 检查是否超时
            if nt - start > self.LOCK_EXPIRE:
                raise TimeOutError('获取锁{}超时！'.format(self.lock_key))
            time.sleep(self.WAIT_INTERVAL)
            if self.logger:
                self.logger.info('getting {} lock, wait {}'.format(self.key, time.time() - nt))

    def release(self):
        """
        acquire保证同时只有一个客户端获得锁，因此这里直接删除
        :return:
        """
        self._redlock.unlock(self._lock)
