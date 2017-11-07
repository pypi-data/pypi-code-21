# -*- coding: utf-8 -*-

import logging
import sys

logger = logging.getLogger('umfpayservice')

try:
    import json
except ImportError:
    import simplejson as json

if not (json and hasattr(json, 'dumps')):
    if not json:
        raise ImportError("umfpayservice扩展包需要安装一个JSON库，"
                          "请安装json库(3.0以下)或者somplejson(3.0以上)"
                          "你可以使用pip install simplejson或者easy_install simplejson来安装")

try:
    import json
except ImportError:
    json = None

if not (json and hasattr(json, 'loads')):
    try:
        import simplejson as json
    except ImportError:
        raise ImportError("umfpayservice扩展包需要安装一个JSON库，"
                          "请安装json库(3.0以下)或者samplejson(3.0以上)"
                          "你可以使用pip install simplejson或者easy_install simplejson来安装")

try:
    import urllib.parse as urllib_parser
except ImportError:
    import urllib as urllib_parser

try:
    import cStringIO as StringIO
except ImportError:
    from io import StringIO

# def api_encode(data):
#     for key, value in data.items():
#         yield (utf8(key), utf8(value))

def url_encode(params):
    return urllib_parser.urlencode(params)

def convert_url_not_encode(params):
    '''
    转化为key=value&的形式，不进行编码
    :param params: dict
    :return: str params
    '''
    if isinstance(params, list):
        iterable = params
    elif isinstance(params, dict):
        iterable = params.items()
    else:
        raise TypeError("convert_url_not_encode: 不支持该类型的转化。%r" % params)

    result = None
    for key, value in iterable:
        # if value is None or value == '':
        #     continue

        if result is None:
            result = "%s=%s" % (key, value)
        else:
            result = "%s&%s=%s" % (result, key, value)
    return result

def utf8_encode(value):
    return encode(decode(value, "gbk"), "utf-8")

def gbk_encode(value):
    return encode(decode(value, "utf-8"), "gbk")

def encode(value, encoding='utf-8'):
    if sys.version_info < (3, 0):
        if isinstance(value, unicode):
            return value.encode(encoding)
        return value
    else:
        if isinstance(value, str):
            return value.encode(encoding)
        return value

def decode(value, decoding='utf-8'):
    if sys.version_info < (3, 0):
        if isinstance(value, str):
            return value.decode(decoding)
        return value
    else:
        if isinstance(value, bytes):
            return value.decode(decoding)
        return value

def to_string(value):
    if sys.version_info < (3, 0):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value
    else:
        if isinstance(value, bytes):
            return value.decode('utf-8')
        return value
