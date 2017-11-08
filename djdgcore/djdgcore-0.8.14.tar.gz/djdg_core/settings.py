#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/18
 """
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from django.utils.module_loading import import_string


RESPONSE_CONFIG = getattr(settings, 'RESPONSE_CONFIG')
AUTH_TOKEN_FORMAT = getattr(settings, 'AUTH_TOKEN_FORMAT')
MIDDLEWARE_CONFIG = getattr(settings, 'MIDDLEWARE_CONFIG')


core_settings = settings.DJDG_CORE

LOGGER_NAME = core_settings['LOGGER']
USER_PROXY = core_settings.get('USER_PROXY')
USER_MODEL = core_settings.get('USER_MODEL')
if USER_MODEL:
    USER_MODEL['MODEL'] = import_string(USER_MODEL['MODEL'])
PROJECT_NAME = core_settings.get('PROJECT_NAME', '')
EXT_USER = core_settings.get('EXT_USER', {})

if 'RESPONSE_CONFIG' in core_settings:
    RESPONSE_CONFIG = core_settings['RESPONSE_CONFIG']
if 'AUTH_TOKEN_FORMAT' in core_settings:
    AUTH_TOKEN_FORMAT = core_settings['AUTH_TOKEN_FORMAT']
if 'MIDDLEWARE_CONFIG' in core_settings:
    MIDDLEWARE_CONFIG = core_settings['MIDDLEWARE_CONFIG']


if 'USER_SYSTEM' in core_settings and 'COMMON_API' in core_settings:
    user_system_settings = core_settings['USER_SYSTEM']
    common_api_settings = core_settings['COMMON_API']
elif 'USER_SYSTEM' in core_settings:
    user_system_settings = common_api_settings = core_settings['USER_SYSTEM']
elif 'COMMON_API' in core_settings:
    user_system_settings = common_api_settings = core_settings['COMMON_API']
else:
    raise Exception('请填写用户系统和公共模块相关配置！')


cache_settings = core_settings.get('CACHE', {})
cache_token_settings = cache_settings.get('TOKEN', {})


USER_SYSTEM_HOST = user_system_settings['HOST']
USER_SYSTEM_BASE_URL = user_system_settings['BASE_URL']
USER_SYSTEM_PROTOCOL = user_system_settings['PROTOCOL']
USER_SYSTEM_AUTH_APP_ID = user_system_settings.get('APPID')
USER_SYSTEM_AUTH_APP_SECRET = user_system_settings.get('SECRET')
USER_SYSTEM_USER_RESOURCE = user_system_settings.get('USER_RESOURCE')


COMMON_API_HOST = common_api_settings['HOST']
COMMON_API_BASE_URL = common_api_settings['BASE_URL']
COMMON_API_PROTOCOL = common_api_settings['PROTOCOL']
COMMON_API_AUTH_APP_ID = common_api_settings['APPID']
COMMON_API_AUTH_APP_SECRET = common_api_settings['SECRET']


memberbao_settings = core_settings.get('MEMBERBAO', {})
MEMBERBAO_HOST = memberbao_settings.get('HOST')
MEMBERBAO_BASE_URL = memberbao_settings.get('BASE_URL')
MEMBERBAO_PROTOCOL = memberbao_settings.get('PROTOCOL')
MEMBERBAO_AUTH_APP_ID = memberbao_settings.get('APPID')
MEMBERBAO_AUTH_APP_SECRET = memberbao_settings.get('SECRET')