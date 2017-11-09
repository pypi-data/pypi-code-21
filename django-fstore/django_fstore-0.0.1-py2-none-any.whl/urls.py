# -*- coding: utf-8 -*-

"""
baseinfo urls
~~~~~~~~~~~~~

Created on 2017-07-19
@author: www.hshl.ltd
"""

from __future__ import unicode_literals, print_function

from django.conf.urls import patterns, url


from django_store.store import MinioDownloadView, MinioOpenView, MinioSignedView


urlpatterns = patterns(
    'django_store.views',
    url(r'^minio/download/$', MinioDownloadView.as_view(), name='minio_download'),
    url(r'^minio/open/$', MinioOpenView.as_view(), name='minio_open'),
    url(r'^minio/signed/$', MinioSignedView.as_view(), name='minio_signed'),
)
