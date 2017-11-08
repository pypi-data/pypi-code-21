#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/19
 """
from __future__ import unicode_literals, absolute_import
from functools import update_wrapper


def decorate_urlpatterns(urlpatterns, decorator):
    for pattern in urlpatterns:
        if hasattr(pattern, 'url_patterns'):
            decorate_urlpatterns(pattern.url_patterns, decorator)

        if hasattr(pattern, '_callback'):
            pattern._callback = update_wrapper(decorator(pattern.callback), pattern.callback)

    return urlpatterns
