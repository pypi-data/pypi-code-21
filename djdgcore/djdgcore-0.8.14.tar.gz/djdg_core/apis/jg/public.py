#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2017/1/4
 """
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from jpush import JPush


jg_config = settings.JPUSH


client = JPush(
    jg_config['KEY'],
    jg_config['SECRET']
)
