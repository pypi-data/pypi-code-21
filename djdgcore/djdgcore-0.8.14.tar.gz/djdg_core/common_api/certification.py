#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/31
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client


def certificate_idcard(name, identity):
    """
    身份证实名认证
    :param name:
    :param identity:
    :return:
    """
    res = common_client.get_resource('certification')
    ret = res.post.idcard(data={'name': name, 'identity': identity})
    return ret.result


def certificate_bankcard(name, identity, bankcard, tel):
    """
    银行卡实名认证
    :param name:
    :param identity:
    :param bankcard:
    :param tel:
    :return:
    """
    res = common_client.get_resource('certification')
    data = {
        'name': name,
        'identity': identity,
        'bankcard': bankcard,
        'tel': tel
    }
    ret = res.post.bankcard(data=data)
    return ret.result


def bankcard_info(bankcard):
    """
    查询银行卡信息
    :param bankcard:
    :return:
    """
    res = common_client.get_resource('bankcard', app='certification')
    action = 'query/{}'.format(bankcard)
    ret = res.do_request('get', action)
    return ret.data
