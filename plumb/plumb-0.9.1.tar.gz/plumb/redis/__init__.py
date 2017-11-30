"""
Source and Sink implementation using Redis list.
"""

import logging
from ..serializers import JSON


class Source(JSON):
    """Use a Redis list as Source implementation.

    Uses a connected Redis client to pull packages from the backend list. It
    assumes UTF-8 character set for the Redis client.

    TODO: how do blocking/timeouts work?
    """

    def __init__(self, queue_name, *, redis_client=None):
        self.queue_name = queue_name
        self.client = redis_client
        self.log = logging.getLogger('redis.source.{}'.format(queue_name))
        self.log.debug('using Redis list "{}" as backend'.format(self.queue_name))

    def get(self, timeout=None):
        """Return a package, or None, after optional "timeout" seconds.

        If "timeout" is not provided (or is 0 or None), block forever.
        """
        # redis-py automatically handles convertion between None and 0 for
        # timeout, and between list of "list names" and a single name.
        result = self.client.brpop(self.queue_name, timeout=timeout)

        if result is not None:
            _, val = result
            result = self.deserialize(result[1].decode('utf-8'))

        return result


class Sink(JSON):
    """Use a Redis list as Sink backend.

    Uses a connected Redis client to push to the list. It assumes UTF-8
    character set for the Redis client.
    """

    def __init__(self, queue_name, *, redis_client=None):
        self.queue_name = queue_name
        self.client = redis_client
        self.log = logging.getLogger('redis.sink.{}'.format(queue_name))
        self.log.debug('using Redis list "{}" as backend'.format(self.queue_name))

    def put(self, pkg):
        """Put an object in the queue as a JSON string."""
        self.client.lpush(self.queue_name, self.serialize(pkg))
