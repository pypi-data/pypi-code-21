# -*- encoding: utf-8

'''
shuwen.com News API Python SDK. (Python >= 2.6)
'''

try:
    # Python 2
    from urllib2 import urlopen
    from urllib import quote as urlquote
except ImportError:
    # Python 3
    from urllib.request import urlopen
    from urllib.parse import quote as urlquote

import time
import string
import random
import base64
import hmac
import hashlib
import json


def nonce():
    '''
    随机生成 32 位字符串
    '''
    rule = string.ascii_lowercase + string.digits
    str = random.sample(rule, 32)
    return "".join(str)


def sign(key, raw):
    '''
    API 签名算法
    '''
    my_sign = hmac.new(raw.encode('utf-8'),
                       key.encode('utf-8'), hashlib.sha1).digest()
    return base64.b64encode(my_sign).decode('utf-8')


def encode_params(list):
    '''
    URL 参数编码
    '''
    args = []
    for k, v in list:
        try:
            # Python 2
            qv = v.encode('utf-8') if isinstance(v, unicode) else str(v)
        except NameError:
            qv = str(v)
        args.append('%s=%s' % (k, urlquote(qv)))
    return '&'.join(args)


class NewsError(Exception):
    def __init__(self, code, message):
        #: 错误码
        self.code = code
        #: 错误信息
        self.message = message

    def __str__(self):
        error = {'code': self.code, 'message': self.message}
        return str(error)

    def _str_with_body(self):
        error = {'code': self.code, 'message': self.message}
        return str(error)


class Client():
    '''
    初始化 Client
    '''

    def __init__(self, access_key, secret_key):
        if access_key is None or access_key == "":
            raise TypeError("access_key is required")
        self.access_key = access_key

        if secret_key is None or secret_key == "":
            raise TypeError("secret_key is required")
        self.secret_key = secret_key
        self.endpoint = "https://api.xinwen.cn"

    def request(self, path, options=None):
        '''
       统根据 path 获取文件内容
        '''
        if options is None:
            options = {}
        params_dict = dict({
            "access_key": self.access_key,
            "nonce": nonce(),
            "timestamp": int(round(time.time() * 1000)),
        }, **options)

        sorted_dict = [(k, params_dict[k]) for k in sorted(params_dict.keys())]
        params = encode_params(sorted_dict)
        signature = sign(params, self.secret_key + "&")
        if path.startswith("/") is False:
            path = "/" + path
        params = params + "&signature=" + urlquote(signature)
        uri = self.endpoint + path + "?" + params

        res = urlopen(uri)
        if res.getcode() != 200:
            err = NewsError(res.getcode(), "HTTP status code is not 200")
            return (None, err)

        data = res.read()
        try:
            jsondata = json.loads(data.decode('utf-8'))
            if jsondata.get('succeed', False) is False:
                err = NewsError(jsondata.get('code'), jsondata.get('msg'))
                return (None, err)
            else:
                return (jsondata, None)
        except (ValueError, KeyError, TypeError) as error:
            return (None, NewsError("JSONError", error.message))

    def get_category(self):
        '''
        获取新闻分类
        '''
        json, err = self.request("news/category")
        categories = None
        if json is not None:
            data = json.get("data")
            if data is not None:
                categories = data.get("categories")
        return (categories, err)

    def get_all(self, options=None):
        '''
        获取所有新闻
        '''
        json, err = self.request("news/all")
        data = None
        if json is not None:
            data = json.get("data")
        return (data, err)

    def get_hot(self, options=None):
        '''
        获取热门新闻
        '''
        json, err = self.request("news/hot")
        data = None
        if json is not None:
            data = json.get("data")
        return (data, err)

    def get_important(self, options=None):
        '''
        获取重大新闻
        '''
        json, err = self.request("news/important")
        data = None
        if json is not None:
            data = json.get("data")
        return (data, err)

    def search(self, q, options=None):
        '''
        搜索新闻
        '''
        param_dict = {"q": q}
        if options is not None:
            param_dict = dict(param_dict, **options)
        json, err = self.request("news/search", param_dict)
        data = None
        if json is not None:
            data = json.get("data")
        return (data, err)
