#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/6
 """
from __future__ import unicode_literals, absolute_import
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import User as AuthUser
from djdg_core.core_auth.models import OpenUser
from djdg_oauth.oauthcore import getSign
from djdg_core.core_auth.token import get_user_id
from djdg_core.core_auth.token import get_user_by_token


class TokenAuthenticationBackend(ModelBackend):
    """
    token方式验证逻辑
    """
    def authenticate(self, token):
        user = get_user_by_token(token)
        if user.is_authenticated():
            return user
        return None


class OpenAuthenticationBackend(ModelBackend):
    """
    oauth方式认证
    """
    def authenticate(self, body, appid, secret, signature):
        _signature = getSign(body, secret)
        if _signature != signature:
            return None
        user = OpenUser(appid, secret)
        return user


class AuthUserTokenAuthenticationBackend(ModelBackend):
    """
    token方式验证逻辑
    """
    def authenticate(self, token):
        user_id = get_user_id(token)
        if not user_id:
            return None
        user = AuthUser.objects.filter(pk=user_id).first()
        return user
