#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/20
 """
from __future__ import unicode_literals, absolute_import
from django import dispatch


# 支付结果回调事件
pay_result_callback_event = dispatch.Signal(providing_args=['pay_result'])
