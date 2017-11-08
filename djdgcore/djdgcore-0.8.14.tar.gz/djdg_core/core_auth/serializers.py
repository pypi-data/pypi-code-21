#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/12/19
 """
from __future__ import unicode_literals, absolute_import
from django.contrib.auth.models import User
from rest_framework import serializers
from djdg_core.exceptions import PasswordError
from djdg_core.exceptions import DifferentPasswordError


class UserSerializer(serializers.ModelSerializer):
    """
    用户序列化对象
    """
    password = serializers.CharField(allow_blank=True)

    class Meta:
        model = User

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        validated_data['password'] = password
        instance = super(UserSerializer, self).create(validated_data)
        instance.set_password(password)
        instance.save()
        return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super(UserSerializer, self).update(instance, validated_data)
        if password is not None:
            instance.set_password(password)
            instance.save()
        return instance

    def to_representation(self, instance):
        d = super(UserSerializer, self).to_representation(instance)
        d.pop('password')
        return d


class UserViewSerializer(serializers.ModelSerializer):
    """
    用户信息展示
    """
    class Meta:
        model = User


class ChangePasswordUserSerializer(serializers.Serializer):
    """
    修改密码序列化对象
    """
    id = serializers.IntegerField()
    old_password = serializers.CharField()
    password = serializers.CharField()
    rep_password = serializers.CharField()

    class Meta:
        hidden_model = User
        username_field = 'username'

    def validate(self, attrs):
        user = self.meta.hidden_model.objects.get(id=attrs['id'])
        if not user.check_password(attrs['old_password']):
            raise PasswordError(getattr(user, self.meta.username_field))
        if attrs['password'] != attrs['rep_password']:
            raise DifferentPasswordError()
        return attrs

    def create(self, validated_data):
        user = self.meta.hidden_model.objects.get(id=validated_data['id'])
        user.set_password(validated_data['password'])
        user.save()
        return user
