# -*- coding: utf-8 -*-
from django.conf.urls import url, include
from .routers import router


urlpatterns = [
    url(r'^api/', include(router.urls)),
]
