# -*- coding: utf-8 -*-
from allauth_cas.urls import default_urlpatterns

from .provider import ClipperProvider

urlpatterns = default_urlpatterns(ClipperProvider)
