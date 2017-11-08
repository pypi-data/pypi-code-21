#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/18
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import filters
from django_filters import Filter
from djdg_core.forms.fields import TimestampField


class TimestampFilter(Filter):
    """
    时间戳类型的filter
    """
    field_class = TimestampField


class SelectRelatedFilterBackend(filters.BaseFilterBackend):
    """
    增加select_related参数
    """
    def filter_queryset(self, request, queryset, view):
        select_related_fields = getattr(view, 'select_related_fields', None)
        if select_related_fields:
            queryset = queryset.select_related(*select_related_fields)
        return queryset
