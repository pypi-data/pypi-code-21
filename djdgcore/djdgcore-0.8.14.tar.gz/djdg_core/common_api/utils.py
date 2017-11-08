#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/10
 """
from __future__ import unicode_literals, absolute_import


def regular_user(user):
    """
    规整用户信息
    :param user:
    :return:
    """
    if not user.get('nickname', None):
        user['nickname'] = user['username']

    if 'userKey' not in user:
        user['userKey'] = None
    return user
