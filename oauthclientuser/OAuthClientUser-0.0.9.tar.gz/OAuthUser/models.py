# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from django.contrib.auth import get_user_model
from django.db import models


# Create your models here.
class TUserExtra(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name='extra',
        verbose_name='关联的用户',
        help_text='关联的用户')

    full_name = models.CharField(
        max_length=200,
        null=True,
        verbose_name='用户的显示名',
        help_text='用户的显示名')

    phone_number = models.CharField(
        max_length=16,
        null=True,
        verbose_name='用户手机号',
        help_text='用户手机号')

    access_token = models.CharField(
        max_length=50,
        null=True,
        verbose_name='接入token',
        help_text='授权服务器的接入token')

    expires_in = models.PositiveIntegerField(
        default=0,
        verbose_name='超时时间',
        help_text='ACCESS TOKEN的超时时间')

    start_time = models.DateTimeField(
        auto_now_add=True,
        verbose_name='开始时间',
        help_text='ACCESS TOKEN的开始计时时间')

    token_type = models.CharField(
        max_length=20,
        null=True,
        verbose_name='TOKEN类型',
        help_text='TOKEN类型')

    scope = models.CharField(
        max_length=50,
        null=True,
        verbose_name='权限范围',
        help_text='权限范围')

    refresh_token = models.CharField(
        max_length=50,
        null=True,
        verbose_name='REFRESH TOKEN',
        help_text='可以用它来刷新TOKEN')

    remote_privileges = models.TextField(
        null=True,
        verbose_name='认证服务器返回的权限列表',
        help_text='认证服务器返回的权限列表')

    local_privileges = models.TextField(
        null=True,
        verbose_name='本地记录的权限列表',
        help_text='本地记录的权限列表')

    class Meta:
        db_table = 't_oauth_user_extra'
        app_label = 'OAuthUser'
        verbose_name = '认证用户附加信息'
        verbose_name_plural = '认证用户附加信息'


class TUserAccessToken(models.Model):
    access_token = models.TextField(
        null=True,
        verbose_name='ACCESS_Token',
        help_text='ACCESS_Token')

    user = models.ForeignKey(
        get_user_model(),
        null=True,
        on_delete=models.CASCADE,
        verbose_name='关联的用户',
        help_text='关联的用户')

    recheck_after = models.DateTimeField(
        default=datetime.now,
        verbose_name='重新验证时间',
        help_text='超过这个时间，客户端还带这个token的话，重新到授权服务器校验')

    class Meta:
        db_table = 't_user_access_token_cache'
        app_label = 'OAuthUser'
        verbose_name = '用户AccessToken缓存'
        verbose_name_plural = '用户AccessToken缓存'



