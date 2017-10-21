# -*- coding: utf-8 -*-
"""
rate limiting with leaky bucket algorithm
"""
import time
import logging

__author__ = 'christian'
__created__ = '06.08.17'


class LeakyBucketRateLimiter(object):
    """
    Leaky Bucket Algorithm based rate limiter including a hourly bucket limit

    >>> from ratelimit.leakybucket import LeakyBucketRateLimiter
    >>> from redis import StrictRedis
    >>> redis = StrictRedis()
    >>> limiter = LeakyBucketRateLimiter(redis)
    >>> limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer")

    >>> for i in xrange(11):
    ...     print(limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer"))
    ...
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (False, 0.985522985458374)
    >>> for i in xrange(11):
    ...     print(limiter.acquire("my_request", 10, 1000, 20, consumer_name="Consumer"))
    ...
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (True, 0)
    (False, 3563.840945959091)
    """
    HOURLY_EXPIRE = 60 * 60  # a complete hour has 3600 seconds

    def __init__(self, redis, ):
        """
        rate limiter will use a redis connection

        :param redis: Redis Connection object i.e. StrictRedis
        """
        self.logger = logging.getLogger(__name__)
        self.redis = redis

    def acquire(self, request_name, max_amount, restore_rate, max_hourly, consumer_name="default"):
        """
        acquire a free bucket for the given request

        :param request_name: api request name
        :param max_amount: maximum amount of request (bucket size)
        :param restore_rate: restore rate for this request (leaking) in milli seconds
                             the time one item will be available again in the bucket
                             i.e. 5 items per second = 200 milliseconds
        :param max_hourly: maximum request amount per hour
        :type max_hourly: int
        :param consumer_name: optional consumer name (defaults to "default")
                              to handle multiple consumers
        :returns: True if allowed or false if blocked + blocking time
        :rtype: tuple
        """
        self.logger.info("%s::acquire: [request: %s] [consumer: %s]",
                         self.__class__.__name__, request_name, consumer_name)
        success, wait_time = self._make_ping(request_name, max_amount, restore_rate, max_hourly,
                                             consumer_name)
        self.logger.info("%s::acquire: [request: %s] [consumer: %s] [success: %s] [wait_time: %s]",
                         self.__class__.__name__, request_name, consumer_name, success, wait_time)
        return success, wait_time

    def _make_ping(self, request_name, max_amount, restore_rate, max_hourly, consumer_name):
        """
        test whether to make a request or if requests are limited for this call

        :param request_name: api request name
        :param max_amount: maximum amount of request (bucket size)
        :param restore_rate: restore rate for this request (leaking) in milli seconds
                             the time one item will be available again in the bucket
                             i.e. 5 items per second = 200 milliseconds
        :param max_hourly: maximum request amount per hour
        :type max_hourly: int
        :param consumer_name: consumer name (defaults to "default")
                              to handle multiple consumers
        :return: True if allowed, false if blocked + wait_time
        """
        restore_rate = float(restore_rate) / float(1000)
        log_key = "{consumer_name}:{request_name}".format(consumer_name=consumer_name,
                                                          request_name=request_name)
        hourly_log_key = "hourly_" + log_key
        lock_key = "{log_key}:lock".format(log_key=log_key)
        ttl = max(int(max_amount * restore_rate), 1)  # ttl at least 1 second
        self.logger.debug("%s::_make_ping: start for [log_key: %s] with [max_amount: %s] and "
                          "[restore_rate: %s] and [hourly: %s]",
                          self.__class__.__name__, log_key, max_amount, restore_rate, max_hourly)

        with self.redis.lock(lock_key, timeout=10):
            self.logger.debug("%s::_make_ping: locked for [lock_key: %s]",
                              self.__class__.__name__, lock_key)
            time_now = time.time()
            last_elem = self.redis.lindex(log_key, 0)
            oldest_elem = self.redis.lindex(log_key, -1)
            list_size = self.redis.llen(log_key)
            hourly_list_size = self.redis.llen(hourly_log_key)
            hourly_first = self.redis.lindex(hourly_log_key, -1)
            self.logger.debug("%s::_make_ping: [list_size: %s] [hourly_list_size: %s]",
                              self.__class__.__name__, list_size, hourly_list_size)
            is_full, wait_time = self._hourly_list_full(hourly_log_key, hourly_list_size,
                                                        max_hourly, hourly_first, time_now)
            if is_full:
                return False, wait_time

            is_full, wait_time = self._list_full(list_size, max_amount, last_elem,
                                                 oldest_elem, time_now)
            if is_full:
                return False, wait_time

            expire_time = time_now + restore_rate  # new element will expire after restore time
            if list_size > 0:
                last_elem = float(last_elem)
                if last_elem > time_now:
                    # new element will expire after the previous element has expired + restore time
                    expire_time = last_elem + restore_rate

            self.logger.debug("%s::_make_ping: list free, new element [expire_time: %s]",
                              self.__class__.__name__, expire_time)

            self._set_new_expiry(
                log_key, hourly_log_key, expire_time, max_amount, hourly_list_size, ttl
            )
            return True, 0

    def _hourly_list_full(self, hourly_log_key, hourly_list_size, max_hourly, hourly_first,
                          time_now):
        """
        returns a True + wait_time > 0 if the hourly list is full, False + 0 otherwise

        :param hourly_log_key: redis key for hourly bucket
        :param hourly_list_size: current number of elements in the hourly bucket
        :type hourly_list_size: int
        :param max_hourly: hourly bucket size
        :type max_hourly: int
        :param hourly_first: oldest element (timestamp) of the hourly bucket
        :param time_now: current timestamp
        :type time_now: float
        :returns: bool + wait_time in seconds
        :rtype: tuple
        """
        if hourly_list_size >= max_hourly:
            hourly_end = float(hourly_first) + self.HOURLY_EXPIRE
            self.logger.debug(
                "%s::_hourly_list_full: [start: %s] [end: %s]",
                self.__class__.__name__, hourly_first, hourly_end)
            if time_now <= hourly_end:
                wait_time = hourly_end - time_now
                self.logger.debug("%s::_hourly_list_full: list blocked [wait_time: %s]",
                                  self.__class__.__name__, wait_time)
                return True, wait_time
            else:
                self.redis.delete(hourly_log_key)
        return False, 0

    def _list_full(self, list_size, max_amount, last_elem, oldest_elem, time_now):
        """
        returns a True + sleeptime > 0 if the list is full, False + 0 otherwise

        :param list_size: current number of elements in the bucket
        :type list_size: int
        :param max_amount: bucket size
        :type max_amount: int
        :param last_elem: newest element (timestamp) of the bucket
        :param oldest_elem: oldest element (timestamp) of the bucket
        :param time_now: current timestamp
        :type time_now: float
        :returns: bool + sleeptime in seconds
        :rtype: tuple
        """
        if list_size >= max_amount:
            last_elem = float(last_elem)
            oldest_elem = float(oldest_elem)
            time_diff_newest = time_now - last_elem
            time_diff_oldest = time_now - oldest_elem
            self.logger.debug("%s::_list_full: [time_diff_newest: %s] [time_diff_oldest: %s]",
                              self.__class__.__name__, time_diff_newest, time_diff_oldest)
            if time_diff_newest < 0 and time_diff_oldest < 0:
                # the list is blocked if all elements are not expired yet
                wait_time = abs(time_diff_oldest)
                self.logger.debug("%s::_list_full: list blocked [wait_time: %s]",
                                  self.__class__.__name__, wait_time)
                return True, wait_time
        return False, 0

    def _set_new_expiry(self, log_key, hourly_log_key, expire_time, max_amount, hourly_list_size,
                        ttl):
        """
        set new expire times by adding a new element to the lists

        :param log_key: redis bucket key
        :param hourly_log_key: redis key for hourly bucket
        :param expire_time: new expiry timestamp
        :param max_amount: bucket size
        :param hourly_list_size: current number of elements in the hourly bucket
        :type hourly_list_size: int
        :param ttl: time to live for redis bucket in seconds
        :type ttl: int
        """
        self.redis.lpush(log_key, expire_time)
        self.redis.lpush(hourly_log_key, time.time())
        # store at most max_amount elements in the bucket
        self.redis.ltrim(log_key, 0, max_amount - 1)
        # remove the whole bucket if not used anymore, after all elements have expired
        self.redis.expire(log_key, ttl)
        # start a new hourly-bucket session with the first new element and expire after 60 mins
        if hourly_list_size == 0:
            self.redis.expire(hourly_log_key, self.HOURLY_EXPIRE)
