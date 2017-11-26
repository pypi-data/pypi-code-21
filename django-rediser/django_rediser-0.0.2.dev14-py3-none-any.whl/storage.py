# -*- coding: utf-8 -*-
import redis
import json
from .settings import rediser_settings


class RedisStorage:
    _db = None
    _tries = 3

    def __init__(self, host=None, port=None, db=None):
        self._host = host or rediser_settings['REDIS_HOST']
        self._port = port or rediser_settings['REDIS_PORT']
        self._db_num = db or rediser_settings['REDIS_DB']

    def connect(self):
        self._db = redis.StrictRedis(host=self._host, port=self._port, db=self._db_num)

    def execute(self, func_name, *args, **kwargs):
        if not self._db:
            self.connect()
        result = False
        for i in range(self._tries - 1):
            try:
                func = getattr(self._db, func_name, None)
                result = func(*args, **kwargs)
            except (ConnectionError, TimeoutError):
                if i == self._tries:
                    raise
                self.connect()
            else:
                break

        return result

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.execute('set', name, value, ex=ex, px=px, nx=nx, xx=xx)

    def delete(self, names):
        return self.execute('delete', names)

    def get(self, name):
        result = self.execute('get', name)
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        return result

    def sadd(self, name, *values):
        return self.execute('sadd', name, *values)

    def srem(self, name, *values):
        return self.execute('srem', name, *values)

    def smembers(self, name):
        return self.execute('smembers', name)

    def sismember(self, name, value):
        """Return a boolean indicating if ``value`` is a member of set ``name``"""
        return self.execute('sismember', name, value)

    def rpush(self, name, value):
        return self.execute('rpush', name, value)

    def lpop(self, name):
        return self.execute('lpop', name)

    def lrange(self, name, start, end):
        return self.execute('lrange', name, start, end)

    def llen(self, name):
        return self.execute('llen', name)


class RedisJSON(RedisStorage):
    @staticmethod
    def dump(values, single=True):
        def do_dump(_value):
            if isinstance(_value, (list, tuple, dict)):
                try:
                    _value = json.dumps(_value)
                except (TypeError, ValueError):
                    pass  # TODO: raise?
            return _value

        if not single:
            value = []
            for val in values:
                values.append(do_dump(val))
        else:
            value = do_dump(values)

        return value

    @staticmethod
    def load(values, source):
        def do_load(_value):
            try:
                _new_value = json.loads(_value)
                if source:
                    if not isinstance(_new_value, dict):
                        _new_value = {'json': _new_value}
                    _new_value[source] = _value
            except json.decoder.JSONDecodeError:
                _new_value = _value  # TODO: raise?
            return _new_value

        if isinstance(values, (list, tuple)):
            value = []
            for val in values:
                value.append(do_load(val))
        else:
            value = do_load(values)

        return value

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        return self.execute('set', name, self.dump(value), ex=ex, px=px, nx=nx, xx=xx)

    def get(self, name, source=''):
        result = self.execute('get', name)
        if isinstance(result, bytes):
            result = result.decode('utf-8')
        return self.load(result, source)

    def sadd(self, name, *values):
        return self.execute('sadd', name, *self.dump(values, False))

    def srem(self, name, *values):
        # send raw (source) values here. Right functioning with other values not guaranteed (and even worse).
        return self.execute('srem', name, *self.dump(values, False))

    def smembers(self, name, source=''):
        return self.load(self.execute('smembers', name), source)

    def sismember(self, name, value):
        """Return a boolean indicating if ``value`` is a member of set ``name``"""
        # send raw (source) values here. Right functioning with other values not guaranteed (and even worse).
        return self.execute('sismember', name, self.dump(value))

    def rpush(self, name, value):
        return self.execute('rpush', name, self.dump(value))

    def lpop(self, name, source=''):
        return self.load(self.execute('lpop', name), source)

    def lrange(self, name, start, end, source=''):
        return self.load(self.execute('lrange', name, start, end), source)
