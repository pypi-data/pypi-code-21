# -*- coding: utf-8 -*-
import cPickle
from redis.client import list_or_args
from redis.exceptions import RedisError
from exceptions import AttributeError, IndexError
from sqlalchemy import event
from sqlalchemy import inspect
from .. import JSON, implode
import time, datetime
from inspect import isclass, ismethod, isfunction, getargspec, getsource
from flask import current_app as app
from application import db, get_db_engine

cache_life_time = app.config.get('CACHE_LIFE_TIME', 600)


# 条件混合
def cache_slug(*args):
    return ":".join(map(lambda x: x if isinstance(x, basestring) else str(x), args))


class ModelCache(object):
    """缓存对象"""
    name = ""
    __redis = None

    __caches = {}

    @classmethod
    def fetch(cls, name):
        if name in cls.__caches:
            return cls.__caches[name]
        cache = cls(name)
        return cache

    def __init__(self, name):
        redis = app.redisClient
        self.name = name
        self.__redis = redis
        self.__class__.__caches[name] = self

    def serialize(self, val):
        return cPickle.dumps(val)

    def unserialize(self, val):
        return cPickle.loads(val) if isinstance(val, basestring) else None

    def handle(self):
        return self.__redis

    # 清空类相关缓存
    def clear(self, match=None, count=50):
        if match is None:
            return self.__redis.delete(self.name)
        keys = []
        for key, val in self.__redis.hscan_iter(self.name, match=match, count=count):
            keys.append(key)
        if len(keys):
            self.delete(*keys)
        if len(keys) >= count:
            self.clear(match, count)
        return

    # redis set
    def set(self, key, value, ex=None):
        d = {
            "e": (time.mktime(datetime.datetime.now().timetuple()) + ex) if (ex and isinstance(ex, (int,long))) else 0,
            "d": value
        }
        return self.__redis.hset(self.name, key, self.serialize(d))

    # redis mset
    def mset(self, *args, **kwargs):
        if args:
            if len(args) != 1 or not isinstance(args[0], dict):
                raise RedisError('MSET requires **kwargs or a single dict arg')
            kwargs.update(args[0])
        items = {}
        for k, v in kwargs.items():
            items[k] = self.serialize(self.set_data(v, cache_life_time))
        return self.__redis.hmset(self.name, items)

    # redis get
    def get(self, key):
        d = self.unserialize(self.__redis.hget(self.name, key))
        return self.get_data(key, d)

    @staticmethod
    def try_expired(d):
        if d is None:
            return False
        if not d or not isinstance(d, dict):
            return True
        expired = d.get("e", 0)
        if not expired:
            return True
        ts = time.mktime(datetime.datetime.now().timetuple())
        if expired and expired <= ts:
            return True
        return False

    @staticmethod
    def set_data(value, ex=None):
        return {
            "e": (time.mktime(datetime.datetime.now().timetuple()) + ex) if (ex and isinstance(ex, (int, long))) else 0,
            "d": value
        }

    def get_data(self, key, unserialized):
        if unserialized is None:
            return None
        if self.try_expired(unserialized):
            # self.delete(key)
            return None
        if isinstance(unserialized, dict):
            return unserialized.get("d", None)
        return None

    # redis mget
    def mget(self, keys, *args):
        keys = list_or_args(keys, args)
        gets = self.__redis.hmget(self.name, keys)
        for i, v in enumerate(gets):
            gets[i] = self.get_data(keys[i], self.unserialize(v))
        return gets

    # redis delete
    def delete(self, keys, *args):
        keys = list_or_args(keys, args)
        return self.__redis.hdel(self.name, *keys)


class CacheableBase(db.Model):
    """
        通用缓存模型

        class TestModel(CacheableBase):
            __tablename__ = 'test'

    """
    # 抽象模型
    __abstract__ = True
    __session__ = db.session
    # 根据字段作缓存
    __cached_fields__ = []
    # 标记auto_cached
    __auto_cached__ = False

    # stored with ModelCache instance
    __cache__ = None

    # default expires in 10 mimutes
    __cache_expires__ = cache_life_time

    @classmethod
    def cache(cls, subfix="", noconflict=False):
        if cls.__cache__:
            return cls.__cache__
        path = [cls.__module__, cls.__name__]
        if subfix: path.append(subfix)
        path = ".".join(path)
        cls.__cache__ = ModelCache(path if noconflict else cls.__name__)
        return cls.__cache__

    @classmethod
    def get(cls, ident, flush=False):
        """pk取单个数据实例"""
        if not ident:
            return None
        cache = cls.cache()
        slug = cache_slug("PK", ident)
        if not flush:
            cached = cache.get(slug)
            if cached:
                if not hasattr(cls, "__session__"):
                    raise ReferenceError("__session__ haven't bind to %s" % cls.__name__)
                if inspect(cached).persistent:
                    return cached
                return cls.__session__.merge(cached, load=False)

        # 未缓存
        record = None
        if cls.query:
            record = cls.query.get(ident)
            if record:
                cache.set(slug, record, ex=cls.__cache_expires__)
        return record

    @classmethod
    def mget(cls, pks, *args):
        """
        pk批量取数据实例

        Model.mget(1,2,5)
        Model.mget([1,2,4,5])
        @:returns [instance1, instance2, instance3, ..., None ]
        """
        cache = cls.cache()
        # [ id1, id2, id3, ... ]
        pks = list_or_args(pks, args)
        if not len(pks):
            return []
        pslugs = map(lambda k: cache_slug("PK", str(k)), pks)
        # 先尝试缓存命中数据
        caches = cache.mget(pslugs)
        rect = {}
        lost = []
        for i, cached in enumerate(caches, start=0):
            if cached is None:
                lost.append(pks[i])
            else:
                if not hasattr(cls, "__session__"):
                    raise ReferenceError("__session__ haven't bind to %s" % cls.__name__)
                rect[str(pks[i])] = cached if inspect(cached).persistent else cls.__session__.merge(cached, load=False)

        # 未命中的从数据库中取
        pk = cls._pk()
        if len(lost):
            records = cls.query.filter(getattr(cls, pk).in_(lost)).all()
            cachemap = dict()
            for record in records:
                cachemap[cache_slug("PK", record.__dict__[pk])] = record
                rect[str(record.__dict__[pk])] = record
            # 批量缓存
            if len(cachemap):
                cache.mset(cachemap)

        # 按传入的参数顺序返回数据
        return map(lambda k: rect[str(k)] if str(k) in rect else None, pks)

    @classmethod
    def _pk(cls):
        """first primary key"""
        detection = inspect(cls)
        pks = detection.primary_key
        return pks[0].name if len(pks) else None

    @classmethod
    def save(cls, *args, **kwargs):
        """
        保存/修改模型数据
        :param args:
        :param kwargs:
        :return:
        """
        isnew = False
        pk = cls._pk()
        pkid = None
        if pk in kwargs:      # 存在id参数
            pkid = kwargs[pk]
            del kwargs[pk]    # 移除id参数
            if isinstance(pkid, basestring) and pkid.isdigit():
                pkid = int(pkid)
            if not pkid:
                isnew = True    # id参数不规范, 视为新创建
        else:
            isnew = True

        instance = cls() if isnew else cls.get(pkid)

        if not instance:
            # 记录不存在, 新建记录
            instance = cls()
            if pkid is not None:
                kwargs[pk] = pkid

        # 批量设置属性
        instance.setattrs(kwargs)
        cls.__session__.add(instance)
        cls.__session__.commit()
        return instance

    @classmethod
    def delete(cls, pkid):
        """
        删除记录
        :param pkid, 主键值
        """
        # remove db record
        record = cls.get(pkid)
        if record:
            cls.__session__.delete(record)
            # commit
            cls.__session__.commit()
            return True
        else:
            return False

    @classmethod
    def emptyInstance(cls):
        return cls()

    @classmethod
    def auto_increment(cls):
        """
        获取表的auto_increment
        :return:
        """
        result = db.session.execute(
            "SELECT AUTO_INCREMENT FROM information_schema.tables WHERE table_name='%s'" % cls.__tablename__,
            bind=get_db_engine(cls.__bind_key__))
        rows = result.fetchall()
        return rows[0][0] if len(rows) else None


    def setattrs(self, *args, **kwargs):
        """
        批量设置属性
        :param args:
        :param kwargs:
        :return:
        """
        if args:
            if len(args) != 1 or not isinstance(args[0], dict):
                raise AttributeError('set_attrs requires **kwargs or a single dict arg')
            kwargs.update(args[0])

        for k, v in kwargs.items():
            if hasattr(self, k):  # 类有该属性
                setattr(self, k, v)
        return self

    def flush_cache(self):
        """清除实例缓存"""
        cls = self.__class__
        cache = cls.cache()
        pk = cls._pk()
        if pk in self.__dict__:
            cache.delete(cache_slug("PK", self.__dict__[pk]))
        pass

    @classmethod
    def flush_all(cls):
        """清空所有类下缓存"""
        cls.cache().clear()

    def to_json(self):
        """
        转化实例对象为JSON字符串

        :return:
        """
        return JSON.stringify(self)

    def __json__(self):
        """
        默认JSON序列化回调
        :return:
        """
        dict = {}
        for k, v in self.__dict__.iteritems():
            # 过滤下划线的属性
            if k.find("_", 0, 1) == 0:
                continue
            dict[k] = v
        return dict

    @classmethod
    def __modified__(cls, mapper, connection, target):
        """
        修改记录时调用

        :return:
        """
        return True

    @classmethod
    def auto_cached(cls):
        """
        开启自动缓存

        Model.auto_cached()
        """
        if cls.__auto_cached__:
            return

        cls.__auto_cached__ = True

        @event.listens_for(cls, 'after_update')
        def after_update_handel(mapper, connection, target):
            """
            更新缓存
            update, insert, delete 一条记录时, 都会触发该事件
            :param mapper:
            :param connection:
            :param target:
            :return:
            """
            if cls.__modified__(mapper, connection, target) is False:
                return
            target.flush_cache()

        @event.listens_for(cls, 'after_insert')
        def before_insert_handel(mapper, connection, target):
            """
            插入数据前更新缓存
            :param mapper:
            :param connection:
            :param target:
            :return:
            """
            if cls.__modified__(mapper, connection, target) is False:
                return
            target.flush_cache()

        @event.listens_for(cls, 'after_delete')
        def after_delete_handel(mapper, connection, target):
            """
            删除数据后清缓存

            :param mapper:
            :param connection:
            :param target:
            :return:
            """
            if cls.__modified__(mapper, connection, target) is False:
                return
            target.flush_cache()


def cacheable(expire=cache_life_time, noconflict=False):
    _ = {
        "method": None
    }

    def init(method, *args, **kwargs):
        _['method'] = method
        m.func_name = method.__name__
        m._cache_fun = method
        return m

    def m(*args, **kwargs):
        cls = None
        if len(args) > 0:
            a0 = args[0]
            if isclass(a0):
                cls = a0
            elif isclass(a0.__class__):
                cls = a0.__class__
        method = _['method']
        path = slugpath(method, cls, noconflict)
        slug = argslug(method, False,  *args, **kwargs)
        cache = ModelCache.fetch(path)
        cached = cache.get(slug)
        if cached is not None:
            return cached
        # 原接口取数据
        data = method(*args, **kwargs)
        cache.set(slug, data, expire)
        return data

    return init


def flushcache(method, *args, **kwargs):
    fun = method._cache_fun if hasattr(method,"_cache_fun") else None
    if fun:
        cls = None
        # 清空指定参数缓存
        args = list(args)
        if ismethod(method):
            cls = method.im_self
        path = slugpath(fun, cls)
        cache = ModelCache.fetch(path)
        if not len(args) and not len(kwargs):
            # 清空方法缓存
            cache.clear()
            return True

        if cls:
            args.insert(0, cls)
        slug = argslug(fun, True, *args, **kwargs)
        if slug:
            cache.clear(slug)
        return True
    else:
        return False


def slugpath(method, cls=None, noconflict=False):
    path = "Function"
    if cls:
        path = implode(".", [cls.__module__, cls.__name__]) if noconflict else cls.__name__
    path = implode(".", [path, method.__name__])
    return path


def argslug(method, wildcard=False, *args, **kwargs):
    """
    获取参数slug
    :param method
    :param wildcard: 是否通配符模式
    """
    argspec = getargspec(method)
    argnames = argspec.args if argspec.args else () # tuple
    argdef_list = argspec.defaults if argspec.defaults else () # tuple
    argdefs = dict()    # 参数默认值, 字典, 保存有默认值的参数名和值
    defindex = len(argnames) - len(argdef_list)
    for i, defv in enumerate(argdef_list):
        # 绑定默认值
        argdefs[argnames[defindex+i]] = defv

    if len(argnames):
        # 分离第一个参数 @classmethod
        if argnames[0] in kwargs:
            if isclass(kwargs[argnames[0]]):
                kwargs.pop(argnames[0])
                argnames = argnames[1:]

        else:
            if len(args) and isclass(args[0]):
                args = args[1:]
                argnames = argnames[1:]

    slugs = list()
    for i, name in enumerate(argnames):
        v = "*"
        has_value = False
        if kwargs.has_key(name):
            v = kwargs.pop(name)
            has_value = True
        if not has_value and len(args) > i:
            v = args[i]
            has_value = True
        if not wildcard and not has_value and argdefs.has_key(name):
            v = argdefs.get(name)
            has_value = True
        if not wildcard and not has_value:
            continue
        slugs.append("%s=%s" % (name, v))

    if len(args) > len(argnames):
        args = args[len(argnames):]
    else:
        args = []
    for v in args:
        slugs.append("%s" % v)

    kws = kwargs.items()
    kws = sorted(kws, key=lambda kv: kv[0], reverse=False)
    for k, v in kws:
        slugs.append("%s=%s" % (k, v))
    slugs = implode(",", slugs)
    return "("+slugs+")" if slugs else "()"
