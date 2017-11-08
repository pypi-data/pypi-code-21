#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client
from djdg_core.exceptions import ParameterNotExistOrEmptyError
from djdg_core.common_api.utils import regular_user


def register_by_code(code, phoneNumber, introducerCode='', unionid=''):
    """
    通过短信验证码注册
    :param code:
    :param phoneNumber:
    :param introducerCode:
    :param unionid:
    :return:
    """
    res = common_client.get_resource('regist')
    ret = res.post.code(data={
        'code': code,
        'phoneNumber': phoneNumber,
        'introducerCode': introducerCode,
        'unionid': unionid
    })
    return regular_user(ret.data)


def register_by_password(password, phoneNumber, introducerCode='', unionid=''):
    """
    通过密码方式注册
    :param password:
    :param phoneNumber:
    :param introducerCode:
    :param unionid:
    :return:
    """
    res = common_client.get_resource('regist')
    ret = res.post.password(data={
        'password': password,
        'phoneNumber': phoneNumber,
        'introducerCode': introducerCode,
        'unionid': unionid
    })
    return ret.result


def login_by_password(phoneNumber, password='', userkey=''):
    """
    密码方式登录
    :param phoneNumber:
    :param password:
    :param userkey:
    :return:
    """
    if not password and not userkey:
        raise ParameterNotExistOrEmptyError('password')
    res = common_client.get_resource('login')
    ret = res.post.password(data={
        'phoneNumber': phoneNumber,
        'password': password,
        'userkey': userkey
    })
    return regular_user(ret.data)
