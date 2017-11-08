#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/6
 """
from __future__ import unicode_literals, absolute_import
from django.contrib.auth import authenticate
from djdg_core import settings
from django.http.response import JsonResponse
from rest_framework.request import Request
from djdg_core import exceptions
from djdg_core.middleware import ResponseMiddleware
from djdg_oauth.oauthclient import OAuthClient
from djdg_oauth.oauthcore import get_verify_key
from djdg_oauth.oauthcore import getSign
import logging
import json


class AuthenticationMiddleware(object):
    """
    用户认证中间件
    """
    PERMIT_ALL_PARAM = '_permit_all_'

    def __init__(self):
        self.setting = settings.MIDDLEWARE_CONFIG.get(self.__class__.__name__, {})
        self.logger = logging.getLogger(self.setting['LOGGER'])
        self.permit_all_param = self.PERMIT_ALL_PARAM
        self.auth_header_name = self.setting.get('AUTH_HEADER_NAME', 'TOKEN')
        self.auth_token_format = self.setting.get('AUTH_TOKEN_FORMAT', 'session:{token}')
        self.res_mdl_setting = settings.MIDDLEWARE_CONFIG.get(ResponseMiddleware.__name__, {})
        self.status_param = self.res_mdl_setting['STATUS_PARAM']
        self.msg_param = self.res_mdl_setting['MSG_PARAM']
        self.data_param = self.res_mdl_setting['DATA_PARAM']
        self.cors_auth_disable = self.setting.get('CORS_AUTH_DISABLE')

    def process_view(self, request, callback, callback_args, callback_kwargs):
        if self.cors_auth_disable and 'options' == request.method.lower():
            # 跨域时，前端不能往OPTIONS请求中增加TOKEN头，故而此处先忽略
            return None
        if isinstance(request, Request):
            orig_request = request._request
        else:
            orig_request = request
        auth_client = OAuthClient()
        uri, http_method, body, headers = auth_client._extract_params(request)
        signature = headers.get("Authorization")
        if signature:
            ret = self.open_auth(request, body, headers)
        else:
            ret = self.token_auth(orig_request, request)
        # authorization和token均验证不通过，则查看是否是视图允许一切访问
        return None if ret and getattr(callback, self.permit_all_param, None) else ret

    def open_auth(self, request, body, headers):
        err_msg = None
        if isinstance(body, basestring):
            body_obj = json.loads(body)
        else:
            body_obj = body
        appid = body_obj.get("appid")
        keys_obj = None
        if not appid:
            self.logger.error('can not find appid in request body')
            err_msg = '没有找到appid，认证失败！'
        else:
            keys_obj = get_verify_key(appid)
            if not keys_obj:
                self.logger.error('Can not found App [{aid}] secret'.format(aid=appid))
                err_msg = '找不到APP[{aid}]的秘钥！'.format(aid=appid)
        if err_msg or not keys_obj:
            return JsonResponse(
                {
                    self.status_param: exceptions.auth_error.status,
                    self.msg_param: err_msg,
                    self.data_param: exceptions.auth_error.data
                },
                status=401
            )
        signature = headers.get("Authorization")
        request.client_type = keys_obj.app
        user = authenticate(body=body, appid=appid, secret=keys_obj.secret, signature=signature)
        if not user:
            _signature = getSign(body, keys_obj.secret)
            msg = 'App {aid} signature value error [{s1}/{s2}]'.format(
                aid=appid,
                s1=signature,
                s2=_signature
            )
            self.logger.error(msg)
            return JsonResponse(
                {
                    self.status_param: exceptions.auth_error.status,
                    self.msg_param: exceptions.auth_error.msg,
                    self.data_param: exceptions.auth_error.data
                },
                status=401
            )
        request.user = user
        msg = 'App {aid} login with signature {s}'.format(
            aid=user.app_id,
            s=signature
        )
        self.logger.info(msg)

    def token_auth(self, orig_request, request):
        header_token = request.META.get('HTTP_{0}'.format(self.auth_header_name))
        if not header_token:
            self.logger.error('request {rid} has no token'.format(rid=id(request)))
            return JsonResponse(
                {
                    self.status_param: exceptions.auth_error.status,
                    self.msg_param: exceptions.auth_error.msg,
                    self.data_param: exceptions.auth_error.data
                },
                status=401
            )
        only_token = header_token.split(':')[-1]
        auth_token = self.auth_token_format.format(token=only_token)
        try:
            user = authenticate(token=auth_token)
        except Exception as e:
            self.logger.exception(e)
            user = None
        if not user:
            msg = 'Token {token} is invalid in request {rid}.'.format(
                token=header_token,
                rid=id(orig_request)
            )
            self.logger.error(msg)
            return JsonResponse(
                {
                    self.status_param: exceptions.auth_error.status,
                    self.msg_param: exceptions.auth_error.msg,
                    self.data_param: exceptions.auth_error.data
                },
                status=401
            )
        request.user = user
        msg = 'User {uid} login with token {token} in request {rid}.'.format(
            uid=user.id,
            token=header_token,
            rid=id(orig_request)
        )
        self.logger.info(msg)
