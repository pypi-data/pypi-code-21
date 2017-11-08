#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/7/12
 """
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from redis import StrictRedis
from djdg_core.exceptions import StandardResponseError
from redis.exceptions import RedisError
from redis._compat import iteritems
from redis.client import StrictPipeline
import re
import time


class MyStrictRedis(StrictRedis):
    """
    copy from o2o.cache to use REDIS.
    REDIS代理，将用到KEYS方法的KEY放入一个SET，使用KEYS操作时在此SET中查找
    """
    key_patterns = ('.*:column:map:set', '.*:groupon:set',
                    '.*:region:.*:promotion:set', 'seckill:.*',
                    '.*:seckill:set', 'smscode:.*', 'group:buying:*')

    def get_pattern_key(self, key):
        """
        """
        for pattern in self.key_patterns:
            if re.match(pattern, key):
                return pattern
        return None

    def keys(self, pattern='*'):
        pattern_key = self.get_pattern_key(pattern)
        if pattern_key is None:
            return ()

        result = []
        pattern = pattern.replace('*', '.*')
        keys = self.smembers(pattern_key)
        if keys is None:
            return ()
        for key in keys:
            if re.match(pattern, key):
                result.append(key)

        return result

    def add_key(self, key):
        pattern_key = self.get_pattern_key(key)
        if pattern_key is not None:
            super(MyStrictRedis, self).sadd(pattern_key, key)

    def remove_key(self, key):
        pattern_key = self.get_pattern_key(key)
        # print pattern_key,key
        if pattern_key is not None:
            self.srem(pattern_key, key)

    def brpoplpush(self, listname, back_list):
        darr = super(MyStrictRedis, self).brpop(listname)
        if darr is None:
            return None
        data = darr[1]
        super(MyStrictRedis, self).lpush(back_list, data)
        return data

    def execute_command(self, *args, **options):
        try:
            return super(MyStrictRedis, self).execute_command(*args, **options)
        except Exception as e:
            print e.message
            pass

    def clean_keys(self, pattern_key):
        if pattern_key in self.key_patterns:
            names = super(MyStrictRedis, self).smembers(pattern_key)
            if not names:
                names = set()
            names.add(pattern_key)
            super(MyStrictRedis, self).delete(*names)

    def delete(self, *names):
        for name in names:
            self.remove_key(name)
        return super(MyStrictRedis, self).delete(*names)

    def hset(self, name, key, value):
        self.add_key(name)
        return super(MyStrictRedis, self).hset(name, key, value)

    def set(self, name, value, ex=None, px=None, nx=False, xx=False):
        self.add_key(name)
        return super(MyStrictRedis, self).set(name, value, ex, px, nx, xx)

    def rpush(self, name, *values):
        self.add_key(name)
        return super(MyStrictRedis, self).rpush(name, *values)

    def lpush(self, name, *values):
        self.add_key(name)
        return super(MyStrictRedis, self).lpush(name, *values)

    def sadd(self, name, *values):
        # log.info(name)
        self.add_key(name)
        return super(MyStrictRedis, self).sadd(name, *values)


class LimitedRedisKeyManager(object):
    """
    redis method parameter parser
    """
    STRING_COMMANDS = 'APPEND BITCOUNT BITOP DECR DECRBY GET GETBIT GETRANGE GETSET INCR INCRBY INCRBYFLOAT MGET ' \
                      'MSET MSETNX PSETEX SET SETBIT SETEX SETNX SETRANGE STRLEN'
    STRING_GET_VALUE_COMMANDS = 'BITCOUNT GET GETBIT GETRANGE MGET STRLEN'

    HASH_COMMANDS = 'HDEL HEXISTS HGET HGETALL HINCRBY HINCRBYFLOAT HKEYS HLEN HMGET HMSET HSET HSETNX HVALS HSCAN'
    HASH_GET_VALUE_COMMANDS = 'HEXISTS HGET HGETALL HKEYS HLEN HMGET HVALS HSCAN'

    LIST_COMMANDS = 'BLPOP BRPOP BRPOPLPUSH LINDEX LINSERT LLEN LPOP LPUSH LPUSHX LRANGE LREM LSET LTRIM RPOP ' \
                    'RPOPLPUSH RPUSH RPUSHX'
    LIST_GET_VALUE_COMMANDS = 'LINDEX LINSERT LLEN LRANGE LPUSHX LSET LTRIM RPUSHX'

    SET_COMMANDS = 'SADD SCARD SDIFF SDIFFSTORE SINTER SINTERSTORE SISMEMBER SMEMBERS SMOVE SPOP SRANDMEMBER SREM ' \
                   'SUNION SUNIONSTORE SSCAN'
    SET_GET_VALUE_COMMANDS = 'SCARD SDIFF SINTER SISMEMBER SMEMBERS SRANDMEMBER SUNION SSCAN'

    SORTED_SET_COMMANDS = 'ZADD ZCARD ZCOUNT ZINCRBY ZRANGE ZRANGEBYSCORE ZRANK ZREM ZREMRANGEBYRANK ' \
                         'ZREMRANGEBYSCORE ZREVRANGE ZREVRANGEBYSCORE ZREVRANK ZSCORE ZUNIONSTORE ZINTERSTORE ZSCAN'
    SORTED_SET_GET_VALUE_COMMANDS = 'ZCARD ZCOUNT ZRANGE ZRANGEBYSCORE ZRANK ZREVRANGE ZREVRANGEBYSCORE ZREVRANK ' \
                                    'ZSCORE ZSCAN'

    DEL_COMMAND = 'DEL'

    MAYBE_DEL_COMMANDS = 'HDEL ' \
                         'BLPOP BRPOP LPOP LREM RPOP ' \
                         'SPOP SREM ' \
                         'ZREM'

    REDIS_DATA_TYPES = ['string', 'hash', 'list', 'set', 'sorted_set']

    def __init__(self, redis):
        self.redis = redis
        self.command_group_map = {}
        for s, t in zip([self.STRING_COMMANDS, self.HASH_COMMANDS, self.LIST_COMMANDS, self.SET_COMMANDS,
                         self.SORTED_SET_COMMANDS],
                        self.REDIS_DATA_TYPES):
            for c in s.split(' '):
                self.command_group_map[c] = t
        self.get_value_commands = {}
        for s, t in zip([self.STRING_GET_VALUE_COMMANDS, self.HASH_GET_VALUE_COMMANDS, self.LIST_GET_VALUE_COMMANDS,
                         self.SET_GET_VALUE_COMMANDS, self.SORTED_SET_GET_VALUE_COMMANDS], self.REDIS_DATA_TYPES):
            for c in s.split(' '):
                self.get_value_commands[c] = t
        self.maybe_del_commands = {c for c in self.MAYBE_DEL_COMMANDS.split(' ')}

    def remove_from_container(self, *keys):
        if not keys:
            return None
        return self.redis.rem_keys(*keys)

    def put_in_container(self, *keys):
        if not keys:
            return None
        ts = time.time()
        kwargs = {k: ts for k in keys}
        return self.redis.add_keys(**kwargs)

    def detect_and_remove_keys(self, *keys):
        # pipe = self.redis.pipeline()
        # for k in keys:
        #     pipe = pipe.exists(k)
        res = [self.redis.exists(k) for k in keys]
        removable_keys = [k for k, e in zip(keys, res) if not e]
        self.remove_from_container(*removable_keys)

    def detect_and_add_keys(self, *keys):
        res = [self.redis.exists(k) for k in keys]
        add_keys = [k for k, e in zip(keys, res) if e]
        self.put_in_container(*add_keys)

    def manage_keys(self, response, *args):
        cmd, keys, cmd_type = self.extract_command_keys(*args)
        # 只读，不产生新key，跳过
        if not keys:
            return None
        if self.DEL_COMMAND == cmd:
            self.remove_from_container(*keys)
        elif cmd in self.maybe_del_commands:
            self.detect_and_remove_keys(*keys)
        else:
            m = getattr(self, 'manage_{}_keys'.format(cmd_type))
            m(cmd, keys)

    def manage_string_keys(self, cmd, keys):
        self.put_in_container(*keys)

    def manage_hash_keys(self, cmd, keys):
        self.put_in_container(*keys)

    def manage_list_keys(self, cmd, keys):
        if cmd.endswith('RPOPLPUSH'):
            self.detect_and_remove_keys(*[keys[0]])
            self.detect_and_add_keys(*[keys[1]])
        else:
            self.put_in_container(*keys)

    def manage_set_keys(self, cmd, keys):
        self.put_in_container(*keys)

    def manage_sorted_set_keys(self, cmd, keys):
        self.put_in_container(*keys)

    def extract_command_keys(self, *args):
        cmd = args[0]
        # 如果是仅仅获取值，这种是不会产生新的key，直接返回
        if cmd in self.get_value_commands:
            return cmd, [], None
        if self.DEL_COMMAND == cmd:
            return cmd, args[1:], 'key'
        cmd_type = self.command_group_map.get(cmd)
        if not cmd_type:
            return cmd, [], None
        m = getattr(self, 'extract_{}_keys'.format(cmd_type), None)
        if not m:
            return cmd, [], cmd_type
        return cmd, m(cmd, args[1:]), cmd_type

    @classmethod
    def extract_string_keys(cls, cmd, params):
        keys = []
        if 'BITOP' == cmd:
            keys.append(params[2])
        elif cmd.startswith('MSET'):
            keys = [e for i, e in enumerate(params) if not (i % 2)]
        else:
            keys.append(params[0])
        return keys

    @classmethod
    def extract_hash_keys(cls, cmd, params):
        return [params[0]]

    @classmethod
    def extract_list_keys(cls, cmd, params):
        if cmd in ('BLPOP', 'BRPOP'):
            keys = params[:-1]
        elif cmd.endswith('RPOPLPUSH'):
            keys = params[:2]
        else:
            keys = [params[0]]
        return keys

    @classmethod
    def extract_set_keys(cls, cmd, params):
        if cmd in ('SDIFFSTORE', 'SINTERSTORE', 'SUNIONSTORE'):
            keys = params[:]
        elif 'SMOVE' == cmd:
            keys = params[:2]
        else:
            keys = [params[0]]
        return keys

    @classmethod
    def extract_sorted_set_keys(cls, cmd, params):
        keys = [params[0]]
        return keys


class LimitedStrictRedisPipeline(StrictPipeline):
    """
    对于管道模式，照样要把key纳入管理
    """
    def __init__(self, *args, **kwargs):
        self.key_manager = kwargs.pop('key_manager', None)
        super(LimitedStrictRedisPipeline, self).__init__(*args, **kwargs)

    def execute(self, raise_on_error=True, managed=True):
        """
        :param raise_on_error:
        :param managed:
        :return:
        """
        managed_commands = []
        for args, options in self.command_stack:
            _m = options.pop('managed', True)
            if _m and managed:
                managed_commands.append((args, True))
            else:
                managed_commands.append((args, False))
        res = super(LimitedStrictRedisPipeline, self).execute(raise_on_error)
        for r, c in zip(res, managed_commands):
            if not c[1]:
                continue
            self.key_manager.manage_keys(r, c[0])
        return res

    def immediate_execute_command(self, *args, **options):
        managed = options.pop('managed', True)
        res = super(LimitedStrictRedisPipeline, self).immediate_execute_command(*args, **options)
        if managed:
            self.key_manager.manage_keys(res, args)
        return res


class LimitedStrictRedis(StrictRedis):
    """
    受限的redis客户端
    """
    KEYS_CONTAINER = 'limited:redis:keys'

    def __init__(self, *args, **kwargs):
        super(LimitedStrictRedis, self).__init__(*args, **kwargs)
        self.key_manager = LimitedRedisKeyManager(self)

    def execute_command(self, *args, **options):
        """
        重载 execute_command 将操作的key都存储到KEYS_CONTAINER里面
        :param args:
        :param options:
        :return:
        """
        managed = options.pop('managed', True)
        cmd = args[0]
        if not managed:
            return super(LimitedStrictRedis, self).execute_command(*args, **options)
        elif cmd == self.KEYS_CONTAINER:
            raise StandardResponseError(1, '被管理的key不能是{}'.format(self.KEYS_CONTAINER))
        res = super(LimitedStrictRedis, self).execute_command(*args, **options)
        self.key_manager.manage_keys(res, *args)
        return res

    def pipeline(self, transaction=True, shard_hint=None):
        return LimitedStrictRedisPipeline(
            self.connection_pool,
            self.response_callbacks,
            transaction,
            shard_hint,
            key_manager=self.key_manager
        )

    def exists(self, name):
        return super(LimitedStrictRedis, self).execute_command('EXISTS', name)

    __contains__ = exists

    def add_keys(self, *args, **kwargs):
        """
        往key容器里面增加键
        """
        pieces = []
        if args:
            if len(args) % 2 != 0:
                raise RedisError("ZADD requires an equal number of "
                                 "values and scores")
            pieces.extend(args)
        for pair in iteritems(kwargs):
            pieces.append(pair[1])
            pieces.append(pair[0])
        return super(LimitedStrictRedis, self).execute_command('ZADD', self.KEYS_CONTAINER, *pieces)

    def rem_keys(self, *values):
        """
        从key容器里面移除键
        :param values:
        :return:
        """
        return super(LimitedStrictRedis, self).execute_command('ZREM', self.KEYS_CONTAINER, *values)

    def bitop(self, operation, dest, *keys):
        raise StandardResponseError(1, 'bitop 该命令不支持！')

    def msetnx(self, *args, **kwargs):
        raise StandardResponseError(1, 'msetnx 该命令不支持！')

    def blpop(self, keys, timeout=0):
        raise StandardResponseError(1, 'blpop 该命令不支持！')

    def brpop(self, keys, timeout=0):
        raise StandardResponseError(1, 'brpop 该命令不支持！')

    def brpoplpush(self, src, dst, timeout=0):
        raise StandardResponseError(1, 'brpoplpush 该命令不支持！')


class DefaultCacheProxy(object):
    """
    Proxy access to the default Cache object's attributes.

    This allows the legacy `cache` object to be thread-safe using the new
    ``caches`` API.
    """
    def __init__(self):
        self._client = None

    @property
    def client(self):
        if not self._client:
            kwargs = {}
            for k, v in settings.REDIS.items():
                kwargs[k.lower()] = v
            # self._client = MyStrictRedis(**kwargs)
            # self._client = LimitedStrictRedis(**kwargs)
            self._client = StrictRedis(**kwargs)
        return self._client

    def __getattr__(self, name):
        return getattr(self.client, name)


cache = DefaultCacheProxy()
