#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/5
 """
from __future__ import unicode_literals, absolute_import
from django.utils.translation import ugettext as _


class StanderResponseError(Exception):
    """
    标准响应错误，必须包含 status 和 msg 两个字段
    data 为在发生错误的情况下需要给前端返回的数据，一般是没有的。

    0-9999 公共错误代码
    10000-19999 o2o
    20000-29999 商家版
    30000-39999 配送版
    40000-49999 供应链
    """
    def __init__(self, status, msg, data=None):
        self.status = status
        self.msg = msg
        self.data = data
        self.message = msg


auth_error = StanderResponseError(1, _('not authenticated'), {})


class StandardResponseError(StanderResponseError):
    """
    纠正拼写
    """


class ParameterNotExistsError(StanderResponseError):
    """
    参数不存在
    """
    def __init__(self, param):
        msg = _('Parameter {0} dose not exists.').format(param)
        super(ParameterNotExistsError, self).__init__(2, msg)


class ParameterNotExistOrEmptyError(ParameterNotExistsError):
    """
    参数为空或者不存在
    """

    def __init__(self, param, msg=None):
        if msg is None:
            msg = _('Parameter {0} dose not exists or empty.').format(param)
        super(ParameterNotExistsError, self).__init__(2, msg)


rest_error = StanderResponseError(3, _('rest framework error'))

signature_error = StanderResponseError(4, _('signature is not right'))

state_error = StanderResponseError(5, _('state error'))


class ParameterNotPositiveError(StanderResponseError):
    """
    非整数错误
    """
    def __init__(self, param):
        msg = '参数[{}]应该是一个正数！'.format(param)
        super(ParameterNotPositiveError, self).__init__(6, msg)


class UserNotExists(StanderResponseError):
    """
    用户不存在
    """
    def __init__(self, username):
        msg = '用户[{}]不存在！'.format(username)
        super(UserNotExists, self).__init__(7, msg)


class PasswordError(StanderResponseError):
    """
    密码不正确
    """
    def __init__(self, username):
        msg = '用户[{}]的密码不正确！'.format(username)
        super(PasswordError, self).__init__(8, msg)


class TimeOutError(StanderResponseError):
    """
    超时
    """
    def __init__(self, msg, data=None):
        super(TimeOutError, self).__init__(9, msg, data)


class DifferentPasswordError(StanderResponseError):
    """
    两次密码输入不一致
    """
    def __init__(self, data=None):
        super(DifferentPasswordError, self).__init__(10, '两次密码输入不一致!', data)


class CodeVerifyError(StanderResponseError):
    """
    验证码不正确！
    """
    def __init__(self, status=11, data=None):
        super(CodeVerifyError, self).__init__(status, '验证码不正确！', data)


class UserNameExistsError(StanderResponseError):
    """
    用户已经存在！
    """
    def __init__(self, status=12, msg=None, data=None):
        msg = msg if msg else '用户已经存在！'
        super(UserNameExistsError, self).__init__(status, msg, data)


class PermissionError(StanderResponseError):
    """
    权限错误
    """
    def __init__(self, status=13, msg=None, data=None):
        msg = msg if msg else '用户没有权限进行此操作！'
        super(PermissionError, self).__init__(status, msg, data)


class UserNotLoginError(StanderResponseError):
    """
    用户尚未登录
    """
    def __init__(self, status=14, msg=None, data=None):
        msg = msg if msg else '请先登录！'
        super(UserNotLoginError, self).__init__(status, msg, data)