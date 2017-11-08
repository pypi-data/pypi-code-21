#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/26
 """
from __future__ import unicode_literals, absolute_import
from rest_framework.permissions import BasePermission


ALLOW_ANY = 1
EXTERNAL_ONLY = 2
INTERNAL_ONLY = 3


EXTERNAL_USER_TYPE = 1
INTERNAL_USER_TYPE = 2


ALLOW_AMY_METHOD = ('get', 'options')


class SimplePermission(BasePermission):
    def has_permission(self, request, view):
        """
        action = getattr(view, request.method.lower())
        PERMISSION
                    ALLOW_ANY       允许所有类型用户访问
                    EXTERNAL_ONLY  仅客户端登录用户可以访问
                    INTERNAL_ONLY  仅内部系统app用户可以访问
        1 action 定义了 PERMISSION，则按 PERMISSION 来验证

        user_type:  1 外部用户； 2 内部系统app用户
        """
        user_type = getattr(request.user, 'USER_TYPE', None)
        method = request.method.lower()
        action = getattr(view, method)
        action_permission = getattr(action, 'PERMISSION', None)
        if action_permission is None:
            if method in ALLOW_AMY_METHOD:
                action_permission = ALLOW_ANY
            else:
                action_permission = EXTERNAL_ONLY
        if EXTERNAL_ONLY == action_permission and EXTERNAL_USER_TYPE == user_type:
            return True
        elif INTERNAL_ONLY == action_permission and INTERNAL_USER_TYPE == user_type:
            return True
        elif ALLOW_ANY == action_permission:
            return True
        return False


def permit_external_only(view):
    view.PERMISSION = EXTERNAL_ONLY
    return view


def permit_internal_only(view):
    view.PERMISSION = INTERNAL_ONLY
    return view


def allow_any(view):
    view.PERMISSION = ALLOW_ANY
    return view
