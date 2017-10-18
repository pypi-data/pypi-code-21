# -*- coding: utf-8 -*-

import logging
import sys

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
    import urllib.parse as parser
except ImportError:
    import urllib as parser


logger = logging.getLogger('umfpayservice')

try:
    import cStringIO as StringIO
except ImportError:
    from io import StringIO

def url_encode(params):
    return parser.urlencode(params)

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

def utf8(value):
    if sys.version_info < (3, 0):
        if isinstance(value, unicode):
            return value.encode('utf-8')
        return value
    else:
        return value

def deutf8(value):
    if isinstance(value, str) and sys.version_info < (3, 0):
        return value.decode('utf-8')
    else:
        return value
