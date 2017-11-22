# -*- coding: utf-8 -*-

"""
智能问答
"""

from __future__ import unicode_literals, absolute_import

from enum import IntEnum
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import requests

from .utils import get_nonce_signature


class ResponseType(IntEnum):
    """智能问答的响应类型

    * :attr:`common` - `0`: 普通. 通模式交互直接返回交互结果
    * :attr:`advanced` - `1`: 高级. 高级模式返回完整的报文结果，包括分词结果和语义拆解内容等
    """

    common = 0
    advanced = 1


class Request(object):
    """智能问答请求

    :param str app_key: AppKey

    :param str app_sec: Secret
    """

    def __init__(self, app_key, app_sec):
        self._app_key = app_key
        self._app_sec = app_sec

    @property
    def app_key(self):
        """AppKey

        :rtype: str
        """
        return self._app_key

    @property
    def app_sec(self):
        """Secret

        :rtype: str
        """
        return self._app_sec

    def execute(self, question, platform='custom', user_id='', response_type=ResponseType.common):
        """执行一次智能问答

        智能问答接口，基于HTTP协议的类REST调用方式，支持XML输出格式。

        :param str question: 问题内容

            例如：`"您好！"`

        :param str platform: 消息所对应的平台

            有：

            * weixin
            * web
            * custom
            * android
            * ios

        :param str user_id: 用户id，用户和会话判断依据

            例如：`"user0001"`

        :param AskResponseType response_type: 响应类型

            智能交互接口支持普通和高级两种形式：

            * 普通模式交互直接返回交互结果
            * 高级模式返回完整的报文结果，包括分词结果和语义拆解内容等。

        :return: 回答内容

        :rtype: str
        """
        url = 'http://nlp.xiaoi.com/ask.do'
        nonce, signature = get_nonce_signature(
            self._app_key, self._app_sec, urlparse(url).path, 'POST'
        )
        headers = {
            'X-Auth': 'app_key="{}",nonce="{}",signature="{}"'.format(
                self._app_key, nonce, signature
            )
        }
        params = {
            'platform': platform.strip()
        }
        data = {
            'userId': user_id.strip(),
            'question': question.strip(),
            'type': response_type.value
        }
        res = requests.post(
            url=url,
            params=params,
            headers=headers,
            data=data,
        )
        if res.status_code != requests.codes.ok:
            res.raise_for_status()
        return res.text
