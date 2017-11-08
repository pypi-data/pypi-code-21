#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/11/2
 """
from __future__ import unicode_literals, absolute_import
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.response import Response
from djdg_core.memberbao import serializers
from djdg_core.rest_permissions import allow_any
from djdg_core.memberbao import signals


class PayResultViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """
    支付回调结果
    """
    serializer_class = serializers.PayResultSerializer
    queryset = serializers.PayResult.objects

    @allow_any
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        signals.pay_result_callback_event.send(
            None,
            pay_result=serializer.data
        )
        return Response(serializer.data, headers=headers)