# -*- coding: utf-8 -*-

import django

if django.VERSION < (1, 10):
    from django.core.urlresolvers import reverse
else:
    from django.urls import reverse

from navsy.utils import path_utils

import re


URL_PARAMETER_FORMAT_RE = re.compile(r'\{\w+\}|\<\w+\>')


def format_url(url, parameters=None):
    if parameters:
        if isinstance(parameters, (list, tuple, )):
            url = re.sub(URL_PARAMETER_FORMAT_RE, '%s', url)
            url = url % tuple(parameters)
        elif isinstance(parameters, (dict, )):
            url = url.format(**parameters)
    return url


def get_admin_change_url(obj):
    return reverse('admin:%s_%s_change' %
                   (obj._meta.app_label, obj._meta.model_name, ),
                   args=[obj.id])


def reverse_url(path=None):
    if path and path.startswith('/'):
        path = path[1:]
    parameters = {'path': path} if path else None
    url = reverse('navsy-router', kwargs=parameters)
    return url
