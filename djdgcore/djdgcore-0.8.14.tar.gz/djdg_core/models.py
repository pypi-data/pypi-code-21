#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/5/12
 """
from __future__ import unicode_literals, absolute_import
from django.db import models


class DateTimeModel(models.Model):
    """
    时间字段
    """
    ctime = models.DateTimeField('创建时间', auto_now_add=True)
    utime = models.DateTimeField('修改时间', auto_now=True)

    class Meta:
        abstract = True


def get_filter_manager(*args, **kwargs):
    """
    生成一个带过滤器的manager
    :param args:
    :param kwargs:
    :return:
    """
    class FilterManager(models.Manager):
        def get_queryset(self):
            return super(FilterManager, self).get_queryset().filter(*args, **kwargs)
    return FilterManager
