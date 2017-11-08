#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/13
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import serializers
from collections import OrderedDict
import datetime
import time


class ChoicesField(serializers.Field):
    """
    选择数据的字段
    """
    def __init__(self, choices, **kwargs):
        self._choices = OrderedDict(choices)
        self._rel_choices = OrderedDict([[v, k] for k, v in choices])
        super(ChoicesField, self).__init__(**kwargs)

    def to_internal_value(self, data):
        if data in self._choices:
            return data
        v = self._rel_choices.get(data, None)
        if v is not None:
            return v
        msg_list = ['{0}: {1}'.format(v, k) for k, v in self._choices.items()]
        raise serializers.ValidationError("仅接受以下参数 {0}.".format(', '.join(msg_list)))

    def to_representation(self, value):
        return self._choices[value]


class TimestampField(serializers.DateTimeField):
    """
    时间戳，内部表示为datetime，序列化为int
    """
    def to_internal_value(self, data):
        if isinstance(data, int):
            data = datetime.datetime.fromtimestamp(data)
        return super(TimestampField, self).to_internal_value(data)

    def to_representation(self, value):
        return int(time.mktime(value.timetuple()))
