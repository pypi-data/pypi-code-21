#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/6
 """
from __future__ import unicode_literals, absolute_import
from rest_framework.authentication import BaseAuthentication


class SimpleRestAuthentication(BaseAuthentication):
    """
    rest 接口认证，在SessionAuthentication的基础上取出csrf的检查
    """
    def authenticate(self, request):
        user = getattr(request._request, 'user', None)
        if not user or not user.is_authenticated():
            return None
        return (user, None)
