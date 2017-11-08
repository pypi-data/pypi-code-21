#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/12/21
 """
from __future__ import unicode_literals, absolute_import
from django import dispatch


register_event = dispatch.Signal(providing_args=['user'])

login_event = dispatch.Signal(providing_args=['user'])
