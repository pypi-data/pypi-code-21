#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/12/19
 """
from __future__ import unicode_literals, absolute_import
from django.db import transaction
from django.forms.models import model_to_dict
from rest_framework import viewsets
from rest_framework import mixins
from rest_framework.decorators import list_route
from rest_framework.decorators import detail_route
from rest_framework.response import Response
from djdg_core.core_auth import serializers
from djdg_core.exceptions import DifferentPasswordError
from djdg_core.exceptions import CodeVerifyError
from djdg_core.common_api import sms
from djdg_core.exceptions import ParameterNotExistOrEmptyError
from djdg_core.exceptions import UserNameExistsError
from djdg_core.exceptions import UserNotExists
from djdg_core.exceptions import PasswordError
from djdg_core.exceptions import PermissionError
from djdg_core.exceptions import StanderResponseError
from djdg_core.core_auth.decorators import login_required
from djdg_core.core_auth.token import set_token
from djdg_core.core_auth import signals
from djdg_core.rest_permissions import allow_any


class UserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """
    用户视图
    """
    # 保存，更新，创建使用的 序列化对象
    serializer_class = serializers.UserSerializer
    # 修改密码使用的 序列化对象
    change_password_serializer_class = serializers.ChangePasswordUserSerializer
    # 返回给客户端使用的 序列化对象
    view_serializer_class = serializers.UserSerializer
    # 用户基础数据对象集合
    queryset = serializers.User.objects.all()
    # 返回给用户端用户数据集合
    view_queryset = serializers.User.objects.all()
    username_field = 'username'
    foreign_field = 'user'

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        self.verify(request.data, *args, **kwargs)
        user_data = self.register(request.data, *args, **kwargs)
        instance = self.combine(user_data, *args, **kwargs)
        if 'token' not in user_data:
            token = self.create_token(user_data, *args, **kwargs)
            kwargs['token'] = token
        else:
            kwargs['token'] = user_data['token']
        signals.login_event.send(
            None,
            user=instance
        )
        kwargs['user_data'] = user_data
        return self.do_response(instance, *args, **kwargs)

    @list_route(methods=['post'])
    @allow_any
    @transaction.atomic
    def login(self, request, *args, **kwargs):
        """
        登录
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        login_type = self.check(request.data, *args, **kwargs)
        kwargs['login_type'] = login_type
        user_data = self.fetch_user(request.data, *args, **kwargs)
        instance = self.combine(user_data, *args, **kwargs)
        if 'token' not in user_data:
            token = self.create_token(user_data, *args, **kwargs)
            kwargs['token'] = token
        else:
            kwargs['token'] = user_data['token']
        signals.login_event.send(
            None,
            user=instance
        )
        kwargs['user_data'] = user_data
        return self.do_response(instance, *args, **kwargs)

    def create_token(self, user_data, *args, **kwargs):
        return set_token(user_data['id'])

    @login_required
    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.verify_permissions(request, *args, **kwargs)
        instance = self.get_object()
        instance = self.update_user(instance, request.data, partial=True)
        instance = self.update_ext_user(instance, request.data, partial=True)
        return self.do_response(instance)

    @detail_route(methods=['post'])
    @login_required
    @transaction.atomic
    def change_password(self, request, *args, **kwargs):
        """
        修改密码
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.verify_permissions(request, *args, **kwargs)
        instance = self.get_object()
        data = request.data
        data['id'] = instance.id
        chp_ser = self.get_change_password_serializer(data=data)
        chp_ser.is_valid(raise_exception=True)
        chp_ser.save()
        return self.do_response(instance, *args, **kwargs)

    def verify_permissions(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id != request.user.id:
            raise PermissionError()

    def get_change_password_serializer(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return:
        """
        klass = self.change_password_serializer_class
        kwargs['context'] = self.get_serializer_context()
        return klass(*args, **kwargs)

    def update_user(self, instance, user_data, *args, **kwargs):
        """
        更新基本用户信息
        :param instance:
        :param args:
        :param kwargs:
        :return:
        """
        partial = kwargs.pop('partial', False)
        serializer = self.get_serializer(instance=instance, data=user_data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return serializer.instance

    def update_ext_user(self, instance, user_data, *args, **kwargs):
        """
        更新用户扩展信息
        :param instance:
        :param args:
        :param kwargs:
        :return: instance
        """
        return instance

    def check(self, login_data, *args, **kwargs):
        """
        检查登录时的参数，不正确则抛出异常
        :param login_data:
        :param args:
        :param kwargs:
        :return:
        """
        self.verify_fields(login_data, [self.username_field])
        if 'password' in login_data:
            filter_kwargs = {
                self.username_field: login_data[self.username_field]
            }
            user = self.get_queryset().filter(**filter_kwargs).first()
            if not user:
                raise UserNotExists(login_data[self.username_field])
            if not user.check_password(login_data['password']):
                raise PasswordError(login_data[self.username_field])
            return 'password'
        if 'code' in login_data:
            res = sms.code_verify(login_data[self.username_field], login_data['code'])
            if res.get('statusCode', None) != 0:
                ex = CodeVerifyError()
                msg = res.get('msg', None)
                if msg:
                    ex.message = msg
                raise ex
            return 'code'

    def fetch_user(self, login_data, *args, **kwargs):
        """
        拉取基础用户数据
        :param login_data:
        :param args:
        :param kwargs:
        :return: user data dict
        """
        login_type = kwargs.get('login_type')
        filter_kwargs = {
            self.username_field: login_data[self.username_field]
        }
        user = self.get_queryset().filter(**filter_kwargs).first()
        if not user and 'code' == login_type:
            # create user
            for f in ['first_name', 'last_name', 'email', 'password']:
                if f not in login_data:
                    login_data[f] = ''
            user_data = self.register(login_data, *args, **kwargs)
        else:
            user_data = model_to_dict(user)
        return user_data

    @classmethod
    def verify_fields(cls, data, fields):
        """
        验证字段是否存在
        :param data:
        :param fields:
        :return:
        """
        for f in fields:
            if f not in data:
                raise ParameterNotExistOrEmptyError(f)

    def verify(self, user_data, *args, **kwargs):
        """
        验证注册数据的正确性
        :param user_data:
        :param args:
        :param kwargs:
        :return: raise exception if verify failed
        """
        self.verify_fields(user_data, [self.username_field, 'password'])
        password = user_data['password']
        rep_password = user_data.pop('rep_password', None)
        code = user_data.pop('code', None)
        if password:
            if rep_password != password:
                raise DifferentPasswordError()
        elif code:
            res = sms.code_verify(user_data[self.username_field], code)
            if res.get('statusCode', None) != 0:
                ex = CodeVerifyError()
                msg = res.get('msg', None)
                if msg:
                    ex.message = msg
                raise ex
        else:
            raise StanderResponseError(6, '未知错误！')

    def register(self, user_data, *args, **kwargs):
        """
        将基础用户数据和扩展用户数据合并
        :param user_data:
        :param args:
        :param kwargs:
        :return: user data of dict
        """
        filter_kwargs = {
            self.username_field: user_data[self.username_field]
        }
        with transaction.atomic():
            user = self.get_queryset().filter(**filter_kwargs).select_for_update().first()
            if user:
                raise UserNameExistsError()
            serializer = self.get_serializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            signals.register_event.send(
                None,
                user=serializer.instance
            )
            return model_to_dict(serializer.instance)

    def combine(self, user_data, *args, **kwargs):
        """
        合并用户扩展信息
        :param user_data:
        :param args:
        :param kwargs:
        :return: django model instance
        """
        filter_kwargs = {
            self.foreign_field: user_data['id']
        }
        instance = self.get_view_queryset().filter(**filter_kwargs).first()
        if not instance and 'code' == kwargs.get('login_type'):
            instance = self.create_ext_user(user_data, *args, **kwargs)
        if not instance:
            raise UserNotExists(user_data[self.username_field])
        return instance

    def create_ext_user(self, user_data, *args, **kwargs):
        return ''

    def get_view_queryset(self):
        return self.view_queryset.all()

    def do_response(self, instance, *args, **kwargs):
        """
        :param instance:
        :param args:
        :param kwargs:
        :return: response
        """
        serializer = self.get_view_serializer(instance=instance, user_data=kwargs.get('user_data'))
        data = serializer.data
        if 'token' in kwargs:
            data['token'] = kwargs['token']
        return Response(data=data)

    def get_view_serializer(self, *args, **kwargs):
        klass = self.view_serializer_class
        context = self.get_serializer_context()
        context['user_data'] = kwargs.pop('user_data', None)
        kwargs['context'] = context
        return klass(*args, **kwargs)


class BaseUserViewSet(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    # 保存，更新，创建使用的 序列化对象
    serializer_class = serializers.UserSerializer
    # 用户基础数据对象集合
    queryset = serializers.User.objects.all()
    view_serializer_class = serializers.UserViewSerializer

    username_field = 'username'
    verify_field_list = [username_field, 'password']

    @classmethod
    def verify_fields(cls, data, fields):
        """
        验证字段是否存在
        :param data:
        :param fields:
        :return:
        """
        for f in fields:
            if f not in data:
                raise ParameterNotExistOrEmptyError(f)

    def verify(self, user_data, *args, **kwargs):
        """
        验证注册数据的正确性
        :param user_data:
        :param args:
        :param kwargs:
        :return: raise exception if verify failed
        """
        self.verify_fields(user_data, self.verify_field_list)

    def create_user(self, user_data, *args, **kwargs):
        """
        将基础用户数据和扩展用户数据合并
        :param user_data:
        :param args:
        :param kwargs:
        :return: user data of dict
        """
        filter_kwargs = {
            self.username_field: user_data[self.username_field]
        }
        with transaction.atomic():
            user = self.get_queryset().filter(**filter_kwargs).select_for_update().first()
            if user:
                raise UserNameExistsError()
            serializer = self.get_serializer(data=user_data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return serializer.instance

    def get_view_serializer(self, *args, **kwargs):
        klass = self.view_serializer_class
        context = self.get_serializer_context()
        kwargs['context'] = context
        return klass(*args, **kwargs)

    def do_response(self, instance, create_token=True, *args, **kwargs):
        """
        :param instance:
        :param create_token:
        :param args:
        :param kwargs:
        :return: response
        """
        serializer = self.get_view_serializer(instance=instance)
        data = serializer.data
        if create_token:
            data['token'] = set_token(data['id'])
        return Response(data=data)


class TokenUserViewSet(BaseUserViewSet):
    """
    token用户注册与登录
    注：用户只用一个表存储
    """

    @list_route(methods=['post'])
    @allow_any
    @transaction.atomic
    def login(self, request, *args, **kwargs):
        """
        用户名密码登录，用户数据为本地
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        login_data = request.data
        self.verify(login_data)
        filter_kwargs = {
            self.username_field: login_data[self.username_field]
        }
        user = self.get_queryset().filter(**filter_kwargs).first()
        if not user:
            raise UserNotExists(login_data[self.username_field])
        if not user.check_password(login_data['password']):
            raise PasswordError(login_data[self.username_field])
        return self.do_response(user)

    @list_route(methods=['post'])
    @allow_any
    @transaction.atomic
    def register(self, request, *args, **kwargs):
        """
        用户注册，用户名，密码方式
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        self.verify(request.data)
        user = self.create_user(request.data)
        return self.do_response(user)
