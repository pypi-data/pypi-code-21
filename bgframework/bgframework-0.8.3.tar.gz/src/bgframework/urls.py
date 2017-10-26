# -*- encoding:utf-8 -*-
from __future__ import absolute_import

from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^sidebar_collapsed/$', views.sidebar_collapsed, name='sidebar_collapsed'),
    url(r'^login/$', views.login, name="login"),
    url(r'^logout/$', views.logout, name="logout"),
    url(r'^logout/done/$', views.logout_after, name="logout_after"),
]