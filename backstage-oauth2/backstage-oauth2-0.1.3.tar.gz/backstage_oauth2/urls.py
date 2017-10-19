# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

try:
    # Django 1.4+
    from django.conf.urls import patterns, url, include
except ImportError:  # pragma: no cover
    # Django 1.3
    from django.conf.urls.defaults import patterns, url, include

from backstage_oauth2.views import BackstageOAuthCallback, BackstageOAuthRedirect


urlpatterns = patterns(
    '',
    url(r'^login/(?P<provider>backstage)/$',
        BackstageOAuthRedirect.as_view(), name='allaccess-login'),
    url(r'^callback/(?P<provider>backstage)/$',
        BackstageOAuthCallback.as_view(), name='allaccess-callback'),
    url(r'^', include('allaccess.urls')),
)
