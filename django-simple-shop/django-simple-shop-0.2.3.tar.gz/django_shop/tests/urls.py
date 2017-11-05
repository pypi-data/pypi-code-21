# coding=utf-8
from __future__ import absolute_import, unicode_literals

from django.conf.urls import url, include

urlpatterns = [
    url(r'^', include('django_shop.urls',
                      namespace='django_shop',
                      app_name='django_shop')),
]
