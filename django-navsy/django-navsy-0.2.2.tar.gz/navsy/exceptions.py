# -*- coding: utf-8 -*-

import django

if django.VERSION < (1, 10):
    from django.core.urlresolvers import NoReverseMatch
else:
    from django.urls import NoReverseMatch
