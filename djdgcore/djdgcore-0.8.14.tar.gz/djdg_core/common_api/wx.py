#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/2
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.exceptions import StanderResponseError
from djdg_core.common_api.public import common_client


def get_code(wx_redirect, appid):
    """
    发送回调url，以获取code
    :param wx_redirect: 微信回调url
    :param appid:
    :return:
    """
    res = common_client.get_resource('wx')
    res.post.code(data={
        'wxRedirect': wx_redirect,
        'appid': appid
    })


def get_access_token(code, appid, secret):
    """
    通过code获取access_token
    :param code:
    :param appid:
    :param secret:
    :return:
    """
    res = common_client.get_resource('wx')
    data = {
        'code': code,
        'appid': appid,
        'secret': secret
    }
    ret = res.post.oauth(data=data, raise_exception=False)
    result = ret.result
    if 'access_token' not in result:
        raise StanderResponseError(
            result.get('errcode', 500),
            result.get('errmsg', 'error')
        )
    return result['access_token']


def get_userinfo(openid, access_token):
    """
    获取用户信息
    :param openid:
    :param access_token:
    :return:
    """
    res = common_client.get_resource('wx')
    data = {
        'openid': openid,
        'access_token': access_token
    }
    ret = res.post.userinfo(data=data, raise_exception=False)
    result = ret.result
    if result.get('errmsg', None):
        raise StanderResponseError(
            result.get('errcode', 500),
            result.get('errmsg', 'error')
        )
    return result
