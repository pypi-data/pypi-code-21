#!/usr/bin/python
# -*- coding: utf-8 -*-
import json
import uuid
import hashlib


class TradeClient(object):
    def __init__(self, app_key='', app_secret='', api_host='', api_version=''):
        """
        初始化客户端
        :param app_key: 应用key
        :param app_secret: 应用秘钥
        :param api_version: api版本号
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.api_host = api_host
        self.api_version = api_version

    def build_header(self, signature):
        """
        构建请求头
        :param signature: 密文
        :return:请求头
        """
        return {
            "X-Signature": signature,
            "X-Version": self.api_version,
            "X-AppKey": self.app_key,
        }

    def build_params_headers(self, params, request_id, session_id):
        """
        构建请求参数及请求头
        :param params:
        :param request_id:
        :param session_id:
        :return:
        """
        if not request_id:
            request_id = str(uuid.uuid1())
        if not session_id:
            session_id = str(uuid.uuid1())
        params = params or dict()
        params['request_id'] = request_id
        params['session_id'] = session_id

        signature = sign(create_raw(params, self.app_secret))
        headers = self.build_header(signature)
        return params, headers

    def get(self, path, params=None, request_id=None, session_id=None):
        """
        发送get请求
        :param path: 请求路径
        :param params: 请求参数
        :param request_id: 请求id
        :param session_id: 请求session id
        :return: 响应结果
        """
        raise NotImplementedError

    def post(self, path, params=None, request_id=None, session_id=None):
        """
        发送post请求
        :param path: 请求路径
        :param params: 请求参数
        :param request_id: 请求id
        :param session_id: 请求session id
        :return: 响应结果
        """
        raise NotImplementedError

    def close_session(self):
        if hasattr(self, 'session'):
            self.session.close()


def sign(raw):
    """
    md5加签
    :param raw: <str> 明文
    :return: 密文
    """
    md5 = hashlib.md5()
    md5.update(raw.encode('utf-8'))
    return md5.hexdigest().upper()


def verifi_sign(raw, signature):
    """
    md5验签
    :param raw: 明文
    :param signature: 签名
    :return: 验签结果
    """
    _signature = sign(raw)
    return _signature == signature


def create_raw(params, secret):
    """
    组装排序参数生成加密前明文
    :param params: <dict> 参数
    :param secret: 密钥
    :return: 加密前明文
    """
    try:
        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')
    except NameError:
        pass
    params_list = []
    for k in sorted(params):
        value = params.get(k, '')
        if isinstance(params.get(k), (dict, list, tuple)):
            value = json.dumps(value, sort_keys=True)
        params_list.append('%s=%s' % (k, value))
    return '%s&AppSecret=%s' % ('&'.join(params_list), secret)
