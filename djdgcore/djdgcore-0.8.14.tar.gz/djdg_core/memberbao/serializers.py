#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/2
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import serializers
from djdg_core.memberbao.models import PayResult


class PayResultSerializer(serializers.ModelSerializer):
    """
    支付回调结果
    """
    class Meta:
        model = PayResult