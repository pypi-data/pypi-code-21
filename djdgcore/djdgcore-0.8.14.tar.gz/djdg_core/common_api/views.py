#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/10/17
 """
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser
from rest_framework.decorators import list_route
from rest_framework.response import Response
from djdg_core.common_api import sms
from djdg_core.common_api import authentication
from djdg_core.exceptions import ParameterNotExistOrEmptyError
from djdg_core.rest_permissions import allow_any
from djdg_core.common_api import serializers
from djdg_core.common_api import signals
from djdg_core.common_api.file import file_upload


class SmsViewSet(viewsets.ViewSet):
    """
    短信视图
    """
    @list_route(methods=['post'])
    @allow_any
    def code(self, request, *args, **kwargs):
        """
        发送短信验证码
        :param request:
            request.data = {
                'phone': '手机号码，字符串'
            }
        :param args:
        :param kwargs:
        :return:
        """
        phone = request.data.get('phone')
        if not phone:
            raise ParameterNotExistOrEmptyError('phone')
        sms.send_code(phone, content=settings.SMS_TEMPLATE)
        return Response({})

    @list_route(methods=['post'])
    @allow_any
    def voicecode(self, request, *args, **kwargs):
        """
        发送语音验证码
        :param request:
            request.data: {
                'phone': '手机号码，字符串'
            }
        :param args:
        :param kwargs:
        :return:
        """
        phone = request.data.get('phone')
        if not phone:
            raise ParameterNotExistOrEmptyError('phone')
        sms.send_voice(phone)
        return Response({})

    @list_route(methods=['post'])
    @allow_any
    def verify(self, request, *args, **kwargs):
        """
        验证验证码
        :param request:
            request.data: {
                'phone': '',
                'code': ''
            }
        :param args:
        :param kwargs:
        :return:
        """
        phone = request.data.get('phone')
        if not phone:
            raise ParameterNotExistOrEmptyError('phone')
        code = request.data.get('code')
        if not code:
            raise ParameterNotExistOrEmptyError('code')
        sms.code_verify(phone, code)
        return Response({})


class RegisterViewSet(viewsets.GenericViewSet):
    """
    注册相关接口
    """
    serializer_class = serializers.RegisterSerializer

    @list_route(methods=['post'])
    @allow_any
    def code(self, request, *args, **kwargs):
        """
        验证码方式  注册/登录接口
        :param request:
            request.data: {
                'code': '',
                'phoneNumber': '',
                'introducerCode': '',
                'unionid': ''
            }
        :param args:
        :param kwargs:
        :return:
        """
        data = request.data
        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        user = authentication.register_by_code(**data)
        signals.user_login_by_sms_code.send(
            None,
            user=user
        )
        return Response(data=user)


class FileUploadViewSet(viewsets.GenericViewSet):
    parser_classes = (MultiPartParser, )

    @list_route(methods=['post'])
    def upload(self, request, *args, **kwargs):
        """
        文件上传
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        data = {}
        for field, file_obj in request._request.FILES.items():
            url = file_upload((file_obj.name, file_obj, file_obj.content_type))
            data[field] = url
        return Response(data=data)

