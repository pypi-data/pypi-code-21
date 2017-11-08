#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/2
 """
from __future__ import unicode_literals, absolute_import
from django.conf.urls import url
from django.conf.urls import include
from rest_framework.routers import DefaultRouter
from djdg_core.memberbao import views


payresult_router = DefaultRouter()
payresult_router.register('payresult', views.PayResultViewSet, base_name='payresult')


urlpatterns = [
    url('^memberbao/', include(payresult_router.urls), name='payresult'),
]