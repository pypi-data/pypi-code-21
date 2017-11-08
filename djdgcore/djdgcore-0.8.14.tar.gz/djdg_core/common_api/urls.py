#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/19
 """
from __future__ import unicode_literals, absolute_import
from django.conf.urls import include
from django.conf.urls import url
from rest_framework.routers import DefaultRouter
from djdg_core.common_api import views


sms_router = DefaultRouter()
sms_router.register('sms', views.SmsViewSet, base_name='sms')

register_router = DefaultRouter()
register_router.register('register', views.RegisterViewSet, base_name='register')

file_router = DefaultRouter()
file_router.register('files', views.FileUploadViewSet, base_name='files')


urlpatterns = [
    url('^common_api/', include(sms_router.urls), name='sms'),
    url('^common_api/', include(register_router.urls), name='register'),
    url('^common_api/', include(file_router.urls), name='files'),
]
