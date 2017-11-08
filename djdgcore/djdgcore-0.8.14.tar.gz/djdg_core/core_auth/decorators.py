#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/8
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.core_auth.middleware import AuthenticationMiddleware
from functools import update_wrapper
from djdg_core.exceptions import UserNotLoginError


def permit_all_access(view):
    setattr(view, AuthenticationMiddleware.PERMIT_ALL_PARAM, True)
    return view


def login_required(view):
    def wrapper(*args, **kwargs):
        if hasattr(args[0], 'request'):
            request = args[0].request
        else:
            request = args[0]
        if not request.user.is_authenticated():
            raise UserNotLoginError()
        return view(*args, **kwargs)
    return update_wrapper(wrapper, view)