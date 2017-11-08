#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/12/20
 """
from __future__ import unicode_literals, absolute_import
from django.conf.urls import include
from django.conf.urls import url
from djdg_core.core_auth import views
from rest_framework.routers import DefaultRouter
from djdg_core.core_auth.decorators import permit_all_access
from djdg_core.utils.urlpatterns import decorate_urlpatterns


user_router = DefaultRouter()
user_router.register('users', views.UserViewSet, 'user_info')


urlpatterns = [
    url('', include(user_router.urls), name='users')
]

urlpatterns = decorate_urlpatterns(urlpatterns, permit_all_access)
