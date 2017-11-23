# -*- coding: utf-8 -*-

"""
辅助功能
"""

from __future__ import unicode_literals

from hashlib import sha1
from random import choice

__all__ = ['get_nonce_signature']

NONCE_CHARS = \
    [chr(x) for x in range(ord('0'), ord('9') + 1)] + \
    [chr(x) for x in range(ord('A'), ord('Z') + 1)] + \
    [chr(x) for x in range(ord('a'), ord('z') + 1)]

NONCE_SIZE = 40

REALM = 'xiaoi.com'


def get_nonce_signature(key, secret, url, method):
    """计算临时随机串和验证签名

    :param str key: App Key

    :param str secret: App Secret

    :param str url: URL

    :param str method: HTTP method

    :return: ``(nonce, signature)`` 临时随机串和验证签名组成的元组

    :rtype: (str, str)

    iBot Cloud开放接口需要通过签名验证访问，
    签名的过程是将AppKey和Secret以及随机数等参数根据一定的签名规则生成签名值，
    用以防止请求被篡改等情况的出现，签名值计算方法：

    1. 用SHA1将AppKey、Realm（固定值：xiaoi.com）以及Secret值按照“AppKey:Realm:Secret”的格式进行加密。
    2. 用SHA1将Method(值大写，如：POST)和URL按照“Method:URL”的格式进行加密。
    3. 用SHA1将第一二步获取的值和40位随机数按照“HA1:nonce:HA2”的格式进行加密，得到签名值。
    4. 将AppKey、第三步中的40位随机数以及签名值按照app_key="xxx",nonce="xxx",signature="xxx"组装成字符串。
    5. 在请求头中添加Key为X-Auth的键，键值为步骤4中获得的字符串。
    """

    def _ha(*args):
        return sha1(':'.join(args).encode()).hexdigest()

    ha1 = _ha(key, REALM, secret)
    ha2 = _ha(method.strip().upper(), url.strip())
    nonce = ''.join([choice(NONCE_CHARS) for _ in range(NONCE_SIZE)])
    signature = _ha(ha1, nonce, ha2)
    return nonce, signature
