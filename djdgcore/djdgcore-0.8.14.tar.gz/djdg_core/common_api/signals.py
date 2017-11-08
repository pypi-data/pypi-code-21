#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/20
 """
from __future__ import unicode_literals, absolute_import
from django import dispatch


# 用户通过验证码登录或注册事件
user_login_by_sms_code = dispatch.Signal(providing_args=['user'])

# 用户通过密码登录事件
user_login_by_password = dispatch.Signal(providing_args=['user'])

# 用户通过验证码与密码注册事件
user_register_by_password = dispatch.Signal(providing_args=['user'])
