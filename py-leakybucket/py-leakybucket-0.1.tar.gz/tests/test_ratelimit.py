# -*- coding: utf-8 -*-
"""
integration test throttling ratelimit
"""
import time
import unittest

import fakeredis

from ratelimit.leakybucket import LeakyBucketRateLimiter

__author__ = 'christian'
__created__ = '02.09.17'


class LockingFakeRedis(fakeredis.FakeStrictRedis):
    def lock(self, key, timeout=None):
        return LockObject()


class LockObject(object):
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass


class TestLeakyBucketRateLimiter(unittest.TestCase):
    def setUp(self):
        self.redis = LockingFakeRedis()
        self.ratelimiter = LeakyBucketRateLimiter(self.redis)

    def tearDown(self):
        self.ratelimiter.redis.flushdb()

    def test_01_acquire(self):
        request_name = "api.call"
        max_amount = 10
        restore_rate = 1000
        max_hourly = 20

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertEqual(result, (True, 0))

    def test_02_acquire_multiple(self):
        request_name = "api.call"
        max_amount = 10
        restore_rate = 1000
        max_hourly = 20
        for _counter in range(10):
            self.ratelimiter.acquire(
                request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
            )

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])
        time.sleep(restore_rate / 1000)

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertEqual(result, (True, 0))

    def test_03_acquire_multiple_hourly_exceeded(self):
        request_name = "api.call"
        max_amount = 30
        restore_rate = 1000
        max_hourly = 10
        for _counter in range(10):
            result = self.ratelimiter.acquire(
                request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
            )
            self.assertTrue(result[0])

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])
        time.sleep(restore_rate / 1000)
        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])

    def test_04_acquire_multiple_hourly_exceeded_and_reset(self):
        request_name = "api.call"
        max_amount = 30
        restore_rate = 1000
        max_hourly = 10
        for _counter in range(10):
            self.ratelimiter.acquire(
                request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
            )

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])
        time.sleep(restore_rate / 1000)
        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertFalse(result[0])

        self.ratelimiter.HOURLY_EXPIRE = 1  # set hourly expire to 1 second

        result = self.ratelimiter.acquire(
            request_name, max_amount, restore_rate, max_hourly, consumer_name="TEST"
        )
        self.assertTrue(result[0])
