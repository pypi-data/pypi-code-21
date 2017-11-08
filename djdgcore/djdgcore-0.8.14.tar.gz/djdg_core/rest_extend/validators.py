#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/9/30
 """
from __future__ import unicode_literals, absolute_import
from djdg_core.exceptions import ParameterNotPositiveError


class PositiveValidator(object):
    """
    正数验证器
    """
    def set_context(self, serializer_field):
        self.field_name = serializer_field.source_attrs[-1]

    def __call__(self, value):
        if 0 >= value:
            raise ParameterNotPositiveError(self.field_name)