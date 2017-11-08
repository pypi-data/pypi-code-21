#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/2
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.common_api.public import common_client


def get_share_content(share_key):
    """
    获取分享模板
    :param share_key:
    :return:
    """
    res = common_client.get_resource('get', app='share/content')
    ret = res.post(data={'shareKey': share_key})
    return ret.data


def get_share_content_list(appid):
    """
    分享模板查询接口
    :param appid:
    :return:
    """
    res = common_client.get_resource('get', app='share/content')
    ret = res.post.all(data={'appid': appid})
    return ret.data


def save_share_content(share_content):
    """
    编辑分享模板
    :param share_content:
        {
            'iconUrl': '',
            'content': '',
            'linkUrl': '',
            'title': '',
            'sharekey': ''
        }
    :return:
    """
    res = common_client.get_resource('content', 'share')
    ret = res.post.save(data={'shareContent': share_content})
    return ret.data