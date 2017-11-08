#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from django.forms.models import model_to_dict
from django.contrib.auth import get_user_model
from django.utils.module_loading import import_string
from djdg_core import settings
from djdg_core.rest_client import RestClient
import logging
from djdg_core.cache.redis_client import cache
from djdg_core.common_api.user import get_info_by_token


user_sys_client = RestClient(
    host=settings.USER_SYSTEM_HOST,
    base_url=settings.USER_SYSTEM_BASE_URL,
    protocol=settings.USER_SYSTEM_PROTOCOL,
    logger=logging.getLogger(settings.LOGGER_NAME),
    oauth_app_id=settings.USER_SYSTEM_AUTH_APP_ID,
    oauth_app_secret=settings.USER_SYSTEM_AUTH_APP_SECRET
)


def user_fetcher(uid, token):
    """
    获取用户信息
    :param uid:
    :param token:
    :return:
    """
    res = user_sys_client.get_resource(settings.USER_SYSTEM_USER_RESOURCE, token=token)
    ret = res.get(action_to=uid)
    return ret.data


ext_user_cfg = settings.EXT_USER
if ext_user_cfg:
    ext_model = import_string(ext_user_cfg['MODEL'])
    ext_user_cfg['MODEL'] = ext_model


class UserProxy(object):
    """
    用户数据代理
    """
    def __init__(self, uid=None, token=None):
        self.token = token
        self.id = self.pk = uid
        self.__data = None
        self._fetch_id()

    def _fetch_id(self):
        uid = self.id
        if not uid:
            uid = cache.get(self.token)
        if not uid:
            return None
        self.id = self.pk = int(uid)

    @property
    def data(self):
        if self.__data:
            return self.__data
        self.__data = self._fetch_data()
        self.__data['__ext_data'] = self._fetch_ext_data()
        return self.__data

    def _fetch_data(self):
        return user_fetcher(self.id, self.token)

    def __getattr__(self, item):
        if item in self.data:
            return self.data[item]
        elif item in self.data['__ext_data']:
            return self.data['__ext_data'][item]
        raise AttributeError("'{}' object has no attribute '{}'".format(self.__class__.__name__, item))

    def _fetch_ext_data(self):
        if not ext_user_cfg:
            return {}
        ext_model = ext_user_cfg['MODEL']
        foreign_key = ext_user_cfg['FOREIGN_KEY']
        filter_fields = {
            foreign_key: self.id
        }
        ext_ist = ext_model.objects.get(**filter_fields)
        return model_to_dict(ext_ist)


class ModelUserProxy(UserProxy):
    """
    数据模型方式的用户代理
    """
    def _fetch_data(self):
        user_model = get_user_model()
        user = user_model.objects.get(pk=self.id)
        return model_to_dict(user)


class CommonUserProxy(UserProxy):
    """
    公共模块用户代理
    """
    def _fetch_id(self):
        pass

    def _fetch_data(self):
        self.__data = get_info_by_token(self.token)
        self.id = self.pk = self.__data['id']


try:
    _user_proxy_ = import_string(settings.USER_PROXY)
except:
    _user_proxy_ = UserProxy


def get_user_proxy():
    return _user_proxy_
