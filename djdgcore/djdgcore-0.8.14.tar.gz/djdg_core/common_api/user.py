#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client
from djdg_core.common_api.utils import regular_user


def get_info_by_username(username):
    """
    获取用户信息
    :param username:
    :return:
    """
    res = common_client.get_resource('user')
    ret = res.post.info(data={'username': username})
    return regular_user(ret.data)


def get_info_by_token(token):
    """
    通过token获取用户信息
    :param token:
    :return:
    """
    res = common_client.get_resource('user')
    ret = res.post.info(data={}, headers={'token': token})
    return regular_user(ret.data)


def user_info_modify(user_info):
    """
    修改用户信息
    :param user_info:
        {
            'username': '',
            'telephone': '',
            'birth': '',
            'sex': '',
            'email': '',
            'headimgurl': ''
        }
    :return:
    """
    res = common_client.get_resource('user')
    ret = res.post.modify(data=user_info)
    return ret.result
