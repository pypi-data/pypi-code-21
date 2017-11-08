#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/9
 """
from __future__ import unicode_literals, absolute_import
from django.forms.fields import DateTimeField
import datetime


class TimestampField(DateTimeField):
    """
    时间戳字段类
    """
    def to_python(self, value):
        try:
            val = int(value)
            val = datetime.datetime.fromtimestamp(val)
            if val is not None:
                value = val
        except:
            pass
        return super(TimestampField, self).to_python(value)
