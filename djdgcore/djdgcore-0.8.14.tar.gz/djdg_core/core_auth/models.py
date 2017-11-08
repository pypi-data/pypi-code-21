#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/6
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.core_auth.proxy import get_user_proxy


UserProxy = get_user_proxy()


class User(object):
    """
    用户信息封装
    """
    USER_TYPE = 1

    def __init__(self, uid=None, token=None):
        self.__proxy = UserProxy(uid, token)

    def is_authenticated(self):
        return self.id is not None

    def has_perms(self, perms):
        pass

    # @property
    # def perms(self):
    #     if self.__perms:
    #         return self.__perms
    #     res = user_sys_client.get_resource('perms').get(action_to=self.id)
    #     self.__perms = res.data
    #     return self.__perms

    @property
    def is_active(self):
        return True

    def __getattr__(self, item):
        return getattr(self.__proxy, item)


class OpenUser(object):
    """
    OAUTH user
    """
    USER_TYPE = 2

    def __init__(self, app_id, secret):
        self.app_id = app_id
        self.secret = secret

    def is_authenticated(self):
        return True
