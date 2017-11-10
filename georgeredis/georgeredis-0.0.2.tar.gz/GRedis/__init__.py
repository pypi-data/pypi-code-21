# -*- coding: utf-8 -*-

import redis

from .setting import (
    DEFAULT_REDIS_HOST,
    DEFAULT_REDIS_PORT,
    DEFAULT_REDIS_DB,
)
from .utils import random_str

__version__ = '0.0.2'


class GRedisClient(object):
    def __init__(self, host=DEFAULT_REDIS_HOST, port=DEFAULT_REDIS_PORT, db=DEFAULT_REDIS_DB):
        self.redis = redis.Redis(host=host, port=port, db=db)

    def client(self):
        return self.redis

    def keys(self, pattern='*'):
        return self.redis.keys(pattern)

    def random_key(self):
        """
        任意的返回一个key
        :return:
        """
        return self.redis.randomkey()

    def random_more_key(self, count):
        """
        任意的返回多个key
        :param count: 个数
        :return:
        """
        result = []
        for i in range(count):
            result.append(self.random_key())
        return result


# 单例模式
default_client = GRedisClient().client()


class GBase(object):
    """
    所有数据结构的基类
    """
    def __init__(self, key=None, initial=None, client=None):
        self.key = key or random_str()
        self.client = client or default_client
        self.data = initial

    def __getattr__(self, name):
        """
        需要注意的是如果使用这个方法，
        避免再次调用类本身的方法，从而导致函数递归
        :param name:
        :return:
        """
        return self._dispatch(name)

    def _dispatch(self, name):
        """
        函数指定到client中执行
        :param name:
        :return:
        """
        try:
            func = getattr(self.client, name)
        except AttributeError:
            raise
        return lambda *args, **kwargs: func(self.key, *args, **kwargs)

    def delete(self):
        self.client.delete(self.key)

    def rename(self, key_name):
        self.client.rename(self.key, key_name)

    def type(self):
        return self.client.type(self.key)

    def expire(self, seconds):
        self.client.expire(self.key, seconds)

    def expire_ts(self, timestamp):
        self.client.expireat(self.key, timestamp)

    def persist(self):
        self.client.persist(self.key)

    def move(self, db):
        self.client.move(self.key, db)

    def ttl(self):
        return self.client.ttl(self.key)


class GSequence(GBase):
    """
    序列类，包括str list set
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GSequence, self).__init__(key, initial, client)

    def __getitem__(self, item):
        return self.get()[item]

    def __eq__(self, other):
        """
        因为是序列，所以可以直接通过data来进行判断
        像是dict这种无序的，则无法通过data进行比较
        :param other:
        :return:
        """
        return self.data == other.data

    def __cmp__(self, other):
        return self.count() == other.count() and self.data == other.data

    def __gt__(self, other):
        return self.count() > other.count()

    def __lt__(self, other):
        return self.count() < other.count()

    def __ge__(self, other):
        return self.count() >= other.count()

    def __le__(self, other):
        return self.count() <= other.count()


class GList(GSequence):
    """
    列表类，对应Python中的List，Redis中的List
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GList, self).__init__(key, initial or [], client)

    def __contains__(self, item):
        """
        使用in和not in
        :return:
        """
        return item in self.data

    def __add__(self, other):
        """
        正向加法：self + other
        :param other:
        :return:
        """
        if isinstance(other, (set, list, str)):
            return self.data + other
        return self.data + other.data

    def __radd__(self, other):
        """
        反向加法：other + self
        :param other:
        :return:
        """
        if isinstance(other, (set, list, str)):
            return self.data + other
        return self.data + other.data

    def __iadd__(self, other):
        """
        累加：self += other
        :param other:
        :return:
        """
        if isinstance(other, list):
            self.extend(other)
        else:
            self.extend(other.data)
        return self

    def __setitem__(self, key, value):
        self.lset(key, value)

    def __reversed__(self):
        """
        reversed(list)
        :return:
        """
        result = reversed(self.data)
        self.data = result  # 可能存在危险
        return result

    def __len__(self):
        return self.llen()  # 避免使用Python中内置的len()，其时间复杂度为O(n)

    @property
    def data(self):
        return self[:]

    @data.setter
    def data(self, iterable):
        self.ltrim(1, 0)  # 删除所有元素，当数据量大的时候可能会有性能问题，时间复杂度为O(n)
        self.extend(iterable)

    def get(self, start=None, stop=None):
        start = start if start is not None else 0
        stop = stop if stop is not None else self.llen()
        return self.lrange(start, stop)

    def append(self, item):
        self.rpush(item)

    def extend(self, iterable):
        self.rpush(*iterable)

    def count(self):
        return self.llen()

    def index(self, value):
        return self.lindex(value)

    def insert(self, index, p_object):
        """
        在指定位置上插入
        :param index:
        :param p_object:
        :return: 新的长度，如果失败则返回-1
        """
        result = self.linsert('BEFORE', self.index(index), p_object)
        return result

    def insert_before(self, index, p_object):
        self.linsert('BEFORE', self.index(index), p_object)

    def insert_after(self, index, p_object):
        self.linsert('AFTER', self.index(index), p_object)

    def pop(self, index=None):
        self.lset(index, '__deleted__')
        self.lrem('__deleted__', 1)

    def blpop(self, keys, timeout=0):
        """
        弹出第一个非空列表的头元素
        :param keys:
        :param timeout: 阻塞的时间
        :return:
        """
        self._dispatch('blpop')(keys, timeout)

    def brpop(self, keys, timeout=0):
        """
        弹出第一个非空列表的末尾元素
        :param keys:
        :param timeout:
        :return:
        """
        self._dispatch('brpop')(keys, timeout)

    def rpoplpush(self, destination, timeout=0):
        """
        rpop -> lpush
        :param destination:
        :param timeout:
        :return:
        """
        if timeout:
            self._dispatch('brpoplpush')(destination, timeout)
        else:
            self._dispatch('rpoplpush')(destination)

    def remove(self, value, count=1, direction='+'):
        """
        这里不进行遍历删除，而是选择对redis进行操作，再进行赋值原数组
        :param value: 值
        :param count: 个数
        :param direction: 正向+或者反向-
        :return:
        """
        count = count if direction == '+' else -count
        self.lrem(value, count)

    def reverse(self):
        result = reversed(self.data)  # 时间复杂度为O(n)，数据量比较大的时候可能会存在问题
        self.data = result

    def sort(self):
        result = sorted(self.data)  # 时间复杂度为O(nlogn)，数据量比较大的时候可能会存在问题
        self.data = result

    def clear(self):
        self.ltrim(1, 0)


class GSet(GSequence):
    """
    集合类，对应Python的Set，Redis中的set
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GSet, self).__init__(key, initial or {}, client)

    def __contains__(self, item):
        """
        使用in和not in
        :return:
        """
        return self.sismember(item)

    def __add__(self, other):
        """
        self + other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.intersection(other)
        return self.intersection(other.data)

    def __radd__(self, other):
        """
        other + self
        :param other:
        :return:
        """
        if isinstance(other, set):
            return other.intersection(self.data)
        return other.intersection(self.data)

    def __and__(self, other):
        """
        self & other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.intersection(other)
        return self.intersection(other.data)

    def __iand__(self, other):
        """
        self &= other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.intersection_update(other)
        return self.intersection_update(other.data)

    def __sub__(self, other):
        """
        self - other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.difference(other)
        return self.difference(other.data)

    def __rsub__(self, other):
        """
        other - self
        :param other:
        :return:
        """
        if isinstance(other, set):
            return other.difference(self.data)
        return other.difference(self.data)

    def __isub__(self, other):
        """
        self -= other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.difference_update(other)
        return self.difference_update(other.data)

    def __or__(self, other):
        """
        self | other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return other.union(self.data)
        return other.union(self.data)

    def __ior__(self, other):
        """
        self |= other
        :param other:
        :return:
        """
        if isinstance(other, set):
            return self.union_update(other)
        return self.union_update(other.data)

    def __ror__(self, other):
        """
        other | self
        :param other:
        :return:
        """
        if isinstance(other, set):
            return other.union(self.data)
        return other.union(self.data)

    @property
    def data(self):
        return self.smembers()

    @data.setter
    def data(self, iterable):
        self.clear()  # 删除所有元素，当数据量大的时候可能会有性能问题，时间复杂度为O(n)
        if iterable:
            self.add(*iterable)

    def count(self):
        return self.scard()

    def add(self, *args):
        self.sadd(*args)

    def clear(self):
        self.delete()

    def remove(self, *args):
        self.srem(*args)

    def rand_member(self, count):
        """
        返回随机的count个成员
        :param count:
        :return:
        """
        return self.srandmember(count)

    def rand_pop(self):
        """
        随机的弹出，并且进行返回
        :return:
        """
        return self.spop()

    def move(self, other, *args):
        """
        将成员移动到other中
        :param other:
        :param args: 成员
        :return:
        """
        self.smove(other.key, *args)

    def discard(self, *args):
        """
        如果元素存在于集合中，则进行删除
        :param args:
        :return:
        """
        self.srem(*args)

    def difference(self, *args, **kwargs):
        """
        和多个set进行的差集，返回的是一个新的set
        :param args:
        :param kwargs:
        :return:
        """
        return self.data.difference(*args, **kwargs)

    def difference_update(self, *args, **kwargs):
        """
        删除另外一个set中所有的元素
        :param args:
        :return:
        """
        self.data = self.difference(*args, **kwargs)
        return self

    def difference_key(self, *args):
        """
        返回和其他的差集
        :param args: 其他的GSet对象
        :return:
        """
        return self.sdiff((x.key for x in args))

    def difference_key_update(self, *args):
        """
        更新成和其他对象的差集
        :param args: 其他的GSet对象
        :return:
        """
        self.sdiffstore((x.key for x in args))
        return self

    def intersection(self, *args, **kwargs):
        """
        和多个set进行的交集，返回的是一个新的set
        :param args:
        :param kwargs:
        :return:
        """
        return self.data.intersection(*args, **kwargs)

    def intersection_update(self, *args, **kwargs):
        """
        和多个set进行的交集
        :param args:
        :param kwargs:
        :return:
        """
        self.data = self.intersection(*args, **kwargs)
        return self

    def intersection_key(self, *args):
        """
        返回和其他的交集
        :param args: 其他的GSet对象
        :return:
        """
        return self.sinter((x.key for x in args))

    def intersection_key_update(self, *args):
        """
        更新成和其他对象的交集
        :param args: 其他的GSet对象
        :return:
        """
        self.sinterstore((x.key for x in args))
        return self

    def union(self, *args, **kwargs):
        """
        和多个set进行的并集，返回的是一个新的set
        :param args:
        :param kwargs:
        :return:
        """
        return self.data.union(*args, **kwargs)

    def union_update(self, *args, **kwargs):
        """
        和多个set进行的并集
        :param args:
        :param kwargs:
        :return:
        """
        self.data = self.union(*args, **kwargs)
        return self

    def union_key(self, *args):
        """
        返回和其他的GSet对象的并集
        :param args:
        :return:
        """
        return self.sunion((x.key for x in args))

    def union_key_update(self, *args):
        """
        更新成和其他对象的并集
        :param args: 其他的GSet对象
        :return:
        """
        self.sunionstore((x.key for x in args))
        return self


class GString(GSequence):
    """
    字符串类，对应Python中的str，Redis中的String
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GString, self).__init__(key, initial or '', client)

    def __contains__(self, item):
        """
        使用in和not in
        :return:
        """
        return item in self.data

    def __add__(self, other):
        """
        self + other
        :param other:
        :return:
        """
        if isinstance(other, (int, str)):
            return self.data + other
        return self.data + other.data

    def __radd__(self, other):
        """
        other + self
        :param other:
        :return:
        """
        if isinstance(other, (int, str)):
            return other + self.data
        return other.data + self.data

    def __len__(self):
        return self.strlen()

    @property
    def data(self):
        return self[:]

    @data.setter
    def data(self, item):
        self.set(item)

    def count(self):
        """
        注意：值是字符串才行
        :return:
        """
        return self.strlen()

    def append(self, item):
        """
        添加字符串值
        :param item:
        :return:
        """
        self._dispatch('append')(item)

    def decrement_by(self, decrement=1):
        """
        注意：数字才能使用
        :param decrement:
        :return:
        """
        return self.decr(decrement)

    def increment_by(self, increment=1):
        """
        注意：数字才能使用
        :param increment:
        :return:
        """
        return self.incr(increment)

    def increment_float_by(self, increment=1.0):
        """
        注意：加浮点数字才能使用
        :param increment:
        :return:
        """
        return self.incrbyfloat(increment)

    def set(self, value, exist=''):
        """
        如果exist为nx，则表示key已经存在的情况下，不进行任何操作
        :param value:
        :param exist:
        :return:
        """
        if exist == 'nx':
            self.setnx(value)
        else:
            self._dispatch('set')(value)

    def setex(self, value, seconds):
        """
        如果exist为ex，则表示key已经存在的情况下，才可以覆盖
        :param value:
        :param seconds: 时间
        :return:
        """
        self.setex(seconds, value)


class GDict(GBase):
    """
    字典和有序集合的基类
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GDict, self).__init__(key, initial or {}, client)

    def __getitem__(self, item):
        return self.get(item)

    def __cmp__(self, other):
        return self.count() == other.count() and self.data == other.data

    def __gt__(self, other):
        return self.count() > other.count()

    def __lt__(self, other):
        return self.count() < other.count()

    def __ge__(self, other):
        return self.count() >= other.count()

    def __le__(self, other):
        return self.count() <= other.count()


class GHash(GDict):
    """
    哈希类，对应Python中的dict，Redis中的hash
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GDict, self).__init__(key, initial or {}, client)

    def __setitem__(self, key, value):
        self.hset(key, value)

    def __delitem__(self, key):
        self.pop(key)

    def __contains__(self, key):
        return self.has_key(key)

    def __len__(self):
        return self.hlen()

    @property
    def data(self):
        return self.hgetall()

    @data.setter
    def data(self, mapping):
        self.clear()
        self.multi_set(mapping)

    def count(self):
        return self.hlen()

    def set(self, key, value, nx=False):
        if nx:
            self.hsetnx(key, value)
        else:
            self.hset(key, value)

    def multi_set(self, mapping):
        """
        设置多个key
        :param mapping: {key: value, ... }
        :return:
        """
        self.hmset(mapping)

    def get(self, key, default=None):
        if self.has_key(key):
            return self.hget(key)
        else:
            if default:
                return default
            else:
                raise KeyError

    def multi_get(self, keys):
        """
        获取多个key的值
        :param keys:
        :return:
        """
        return self.hmget(keys)

    def clear(self):
        """
        清除所有键值对
        :return:
        """
        if self.keys():
            self.hdel(*self.keys())

    def items(self):
        return self.data.items()

    def keys(self):
        return self.hkeys()

    def values(self):
        return self.hvals()

    def has_key(self, key):
        return self.hexists(key)

    def pop(self, key, default=None):
        if not self.has_key(key):
            if default:
                return default
            else:
                raise KeyError
        else:
            self.hdel(key)

    def incr(self, key, increment=1):
        self.hincrby(key, increment)

    def incr_float(self, key, increment=1.0):
        self.hincrbyfloat(key, increment)

    def update(self, mapping):
        self.multi_set(mapping)


class GZSet(GDict):
    """
    有序集合类，对应Python中的ordereddict，Redis中的zset
    """
    def __init__(self, key=None, initial=None, client=None):
        super(GZSet, self).__init__(key, initial or {}, client)

    def __setitem__(self, member, score):
        self.zadd(member, score)

    def __contains__(self, item):
        """
        使用in和not in
        :return:
        """
        return self.zrank(item) is not None

    def __len__(self):
        return self.zcard()

    @property
    def data(self):
        """
        连同score一起返回
        :return:
        """
        return self.zrange(start=0, end=self.zcard(), withscores=True)

    @data.setter
    def data(self, item):
        self.clear()
        self.zadd(*item)

    def set(self, *args, **kwargs):
        """
        和redis命令中不一样，这里是member, score相互对应
        :param args:
        :param kwargs:
        :return:
        """
        self.zadd(*args, **kwargs)

    def count(self):
        return self.zcard()

    def count_by_score(self, min_score, max_score):
        return self.zcount(min_score, max_score)

    def pop(self, member, default=None):
        if member in self:
            self.zrem(member)
        else:
            if default:
                return default
            else:
                raise KeyError

    def clear(self):
        """
        清除所有的内容
        :return:
        """
        self.remove_members_by_rank(0, self.count())

    def score(self, member):
        return self.zscore(member)

    def rank(self, member, order='ASC'):
        """
        返回成员的排名，可以获取正向的排名或者反向的排名
        :param member:
        :param order:
        :return:
        """
        if order in ('DESC', 'desc'):
            return self.zrevrank(member)
        else:
            return self.zrank(member)

    def incrby(self, member, incrememt=1):
        self._dispatch('zincrby')(member, incrememt)

    def decrby(self, member, decrememt=1):
        self._dispatch('zincrby')(member, -decrememt)

    def members(self, order='ASC', withscores=False):
        """
        返回的是排名有序的成员，asc为升序，desc为降序
        :return:
        """
        if order in ('DESC', 'desc'):
            return self.zrevrange(start=0, end=self.zcard(), withscores=withscores)
        else:
            return self.zrange(start=0, end=self.zcard(), withscores=withscores)

    def members_by_score(self, start, end, order='ASC', withscores=False, offset=None, count=None):
        """
        根据分值来返回成员，注意：正向和反向中的参数顺序不同
        :param start:
        :param end:
        :param order:
        :param withscores:
        :param offset:
        :param count:
        :return:
        """
        if order in ('DESC', 'desc'):
            return self.zrevrangebyscore(end, start, offset, count, withscores)
        else:
            return self.zrangebyscore(start, end, offset, count, withscores)

    def remove_members_by_rank(self, start, end):
        """
        根据选中的排名来删除成员
        :param start:
        :param end:
        :return:
        """
        self.zremrangebyrank(start, end)

    def remove_members_by_score(self, start, end):
        """
        根据选中的分值来删除成员
        :param start:
        :param end:
        :return:
        """
        self.zremrangebyscore(start, end)
