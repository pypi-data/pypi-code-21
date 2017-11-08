#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client


def send_code(phone, content=None):
    """
    发送短信验证码到手机
    :param phone:
    :param content:
    :return:
    """
    res = common_client.get_resource('sms')
    data = {
        'phone': phone
    }
    if content:
        data['content'] = content
    ret = res.post.code(data=data)
    return ret.result


def send_voice(phone):
    """
    发送语音验证码
    :param phone:
    :return:
    """
    res = common_client.get_resource('sms')
    ret = res.post.voicecode(data={'phone': phone})
    return ret.result


def code_verify(phone, code):
    """
    验证码校验
    :param phone:
    :param code:
    :return:
    """
    data = {
        'phone': phone,
        'code': code
    }
    res = common_client.get_resource('code', 'sms')
    ret = res.post.verify(data=data)
    return ret.result
