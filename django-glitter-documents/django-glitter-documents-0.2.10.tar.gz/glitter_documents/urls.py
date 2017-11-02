# -*- coding: utf-8 -*-

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.DocumentListView.as_view(), name='list'),
    url(r'^(?P<slug>[\w-]+)/$', views.DocumentDetailView.as_view(), name='detail'),
    url(
        r'^category/(?P<slug>[-\w]+)/$',
        views.CategoryDocumentListView.as_view(),
        name='category-list'
    ),
]
