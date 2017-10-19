# -*- coding: utf-8 -*-
import requests
from hashlib import md5
from inspect import getargspec
from functools import wraps
from diandao import JSON
from diandao.flask import app

# 单实例缓存
__instances__ = {}


def client_instance(cls):
    """ client 单例缓存
    :param cls:
    :return:
    """
    path = ".".join([cls.__module__, cls.__name__])
    ins = __instances__
    if __instances__.has_key(path):
        return __instances__.get(path)
    __instances__[path] = cls()
    return __instances__.get(path)


def description(method):
    """方法描述说明, 用于生成注释文档

    - dsf
    - sdfaf
    """

    @classmethod
    @wraps(method)
    def execute(cls, *args, **kwargs):
        argspec = getargspec(method)
        argnames = argspec.args[1:] if len(argspec.args) else ()  # tuple
        argdef_list = argspec.defaults if argspec.defaults else ()  # tuple
        argdefs = dict()  # 参数默认值, 字典, 保存有默认值的参数名和值
        defindex = len(argnames) - len(argdef_list)
        args = list(args)
        for i, defv in enumerate(argdef_list):
            # 绑定默认值
            argdefs[argnames[defindex + i]] = defv

        for i, name in enumerate(argnames):
            if not kwargs.has_key(name):
                if len(args):
                    kwargs[name] = args.pop(0)
                else:
                    kwargs[name] = argdefs[name]

        return client_instance(cls).execute(method.func_name, *args, **kwargs)

    return execute


class ClientMeta(type):
    """ Client Meta Class
    """

    def __getattr__(cls, method):
        return getattr(client_instance(cls), method, None)

    def __str__(cls):
        return 'Interface Client <%s>' % (cls.__name__,)


class BaseClient():
    """ Remote Interface Base Client
        创建远程接口客户端, 用于请求远程接口
    """
    __metaclass__ = ClientMeta
    # 远程接口名, 默认为Client的类名去掉"Client"
    __interface__ = None
    # 远程接口API, 可在configs中配置, 配置名为 "CLIENT_%s_API" % self.__interface__
    # 如 http://127.0.0.1:9001/rpc
    __api__ = None

    def __init__(self, interface=None, api=None):
        if interface is None:
            interface = self.__default_interface()
        # class 中未定义__interface__
        if not self.__interface__:
            self.__interface__ = interface
        # __api__ 需要依赖 __interface__
        if api is not None:
            self.__api__ = api
        self.__api__ = self.__default_api()

    def api(self):
        return self.__api__

    def __default_interface(self):
        cn = self.__class__.__name__
        return cn[0:-6]

    def __default_api(self):
        if self.__api__:
            return self.__api__
        api = self.__config_api()
        if not api:
            api = self.__parent_config_api()
        return api

    def __config_api(self):
        if self.__interface__ is None:
            return None
        name = "CLIENT_%s_API" % self.__interface__.upper()
        return app.config.get(name, None)

    def __parent_config_api(self):
        """ 尝试使用父类在configs中的API配置
        :return:
        """
        cls = self.__class__
        if cls.__name__ == "BaseClient":
            return None
        bases = cls.__bases__
        for base in bases:
            inst = client_instance(base)
            if hasattr(inst, "__config_api"):
                api = inst.__config_api()
                if api:
                    return api
                else:
                    return inst.__parent_config_api()
        return None

    def execute(self, method, *args, **kwargs):
        """ 接口执行方法
        """
        pass

    def __getattr__(self, method):
        if method.startswith("__"):
            raise AttributeError("%s has no attribute: %s" % (self, method))

        def callmethod(*args, **kwargs):
            return self.execute(method, *args, **kwargs)

        return callmethod

    pass


class PHPV1Client(BaseClient):
    """ php老接口, 对应if.diandao.org

    """

    version = "0.0.1"

    def __init__(self, *args, **kwargs):
        BaseClient.__init__(self, *args, **kwargs)
        if not self.__api__:
            path = None
            if hasattr(self, "__module_path__"):
                path = self.__module_path__
            else:
                path = self.__interface__
            self.__api__ = "http://if.diandao.org/%s/index.php" % (path.lower())

    def execute(self, method, *args, **kwargs):
        """ 接口执行方法
        """
        if not self.__api__:
            raise Exception("Undefined API for %s" % self.__class__.__name__)
        # 参数数据
        params = dict(
            mod=self.__interface__,
            act=method,
            platform="diandao"
        )
        params.update(**kwargs)
        randkey = []
        pkeys = params.keys()
        pkeys.sort()
        key = pkeys[-1]
        randkey.append("%s%s" % (key, params[key]))
        # 添加干扰
        randkey = "".join(randkey) + "The key for Programming"
        # md5
        randkey = md5(randkey).hexdigest()
        # 前9位字符
        randkey = randkey[0:9]
        # http请求参数
        data = dict(
            randkey=randkey,
            c_version=self.version,
            parameter=JSON.stringify(params)
        )
        res = requests.get(self.api(), data)

        if not res.ok:
            raise Exception(res.reason, res.status_code)

        result = res.json()
        if result['code'] > 0:
            raise Exception("[Error] code:%s; desc:%s" % (result['code'], result['desc']))
        return result['data']


class ApiBaseClient(BaseClient):
    version = "0.0.1"

    def __init__(self, *args, **kwargs):
        BaseClient.__init__(self, *args, **kwargs)
        if not self.__api__:
            path = None
            if hasattr(self, "__module_path__"):
                path = self.__module_path__
            else:
                path = self.__interface__
            self.__api__ = "http://api.diandao.org/%s" % path

    def execute(self, method, *args, **kwargs):
        """ 接口执行方法
        """
        if not self.__api__:
            raise Exception("Undefined API for %s" % self.__class__.__name__)
        # 参数数据
        params = dict()
        params.update(**kwargs)
        res = requests.get("%s/%s" % (self.api(), method), params)
        if not res.ok:
            raise Exception(res.reason, res.status_code)
        result = res.json()
        if result['error']:
            raise Exception("[Error] code:%s; desc:%s" % (result['error']['code'], result['error']['message']))
        return result['data']


