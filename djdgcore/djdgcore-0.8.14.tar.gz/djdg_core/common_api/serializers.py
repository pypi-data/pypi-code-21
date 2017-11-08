#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/19
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import serializers
from djdg_core.exceptions import StanderResponseError
from djdg_core.common_api import errors


class RegisterSerializer(serializers.Serializer):
    """
    注册相关参数的校验
    """
    code = serializers.CharField(required=True)
    password = serializers.CharField(required=False)
    rep_password = serializers.CharField(required=False)
    phoneNumber = serializers.CharField(required=True)
    introducerCode = serializers.CharField(required=False)
    unionid = serializers.CharField(required=False)

    def validate(self, attrs):
        password = attrs.get('password')
        rep_password = attrs.get('rep_password')
        if password and rep_password and password != rep_password:
            raise StanderResponseError(
                errors.REPEAT_PASSWORD_NOT_RIGHT,
                '两次输入的密码不一致！'
            )
        return attrs


class LoginSerializer(serializers.Serializer):
    """
    登录相关参数的校验
    """
    phoneNumber = serializers.CharField(required=True)
    password = serializers.CharField(required=True)
    userkey = serializers.CharField(required=False)
