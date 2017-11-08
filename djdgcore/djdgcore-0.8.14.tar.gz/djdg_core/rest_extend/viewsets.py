#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/22
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import viewsets
from rest_framework.response import Response


class NoneOptionsViewSet(viewsets.GenericViewSet):
    """
    options返回空的视图
    """
    def options(self, request, *args, **kwargs):
        return Response(data={})
