#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/5
 """
from __future__ import unicode_literals, absolute_import
from djdg_core import settings
from django.http.response import FileResponse
from django.http.response import JsonResponse
from django.http.response import HttpResponse
from django.utils.translation import ugettext as _
from django.utils.encoding import force_unicode
from rest_framework.response import Response
from djdg_core.exceptions import StanderResponseError
from djdg_core.exceptions import rest_error
import logging
import StringIO
import re
import types
import json
from collections import OrderedDict


class LogMiddleware(object):
    """
    记录请求与响应日志，该中间件请放在第一个
    """
    default_headers = ['Content-Type', 'Content-Length']

    def __init__(self):
        self.setting = settings.MIDDLEWARE_CONFIG[self.__class__.__name__]
        self.logger = logging.getLogger(self.setting['LOGGER'])
        self.request_log_level = self.setting.get('REQUEST_LOG_LEVEL', logging.INFO)
        self.response_log_level = self.setting.get('RESPONSE_LOG_LEVEL', logging.INFO)
        self.text_max_length = self.setting.get('TEXT_MAX_LENGTH', 512)
        valuable_headers = list(self.setting.get('VALUABLE_HEADERS', []))
        self.valuable_headers = {}
        for h in (self.default_headers + valuable_headers):
            _h = h.replace('-', '_').upper()
            self.valuable_headers[_h] = h
        self.text_reg = re.compile('text|json')
        self.json_reg = re.compile('json')

    def process_request(self, request):
        """
        将请求信息写入日志
        request: from address post
        uri: http://www.thy360.com
        headers: content_type: text/plain; content_length: 22 ...
        body:
        post: k=v,
        file: file-name;file name

        :param request:
        :return:
        """
        log_cnt = StringIO.StringIO()
        log_cnt.write('request [{rid}]: from {address} {method}\n'.format(
            rid=id(request),
            address=request.META['REMOTE_ADDR'],
            method=request.method
        ))
        log_cnt.write('uri: {uri}\n'.format(uri=request.get_raw_uri()))
        headers = []
        for h, _h in self.valuable_headers.items():
            v = request.META.get(h)
            headers.append('{h}: {v}'.format(h=_h, v=v))
        log_cnt.write('headers: {headers}\n'.format(headers='; '.join(headers)))
        content_type = request.META.get('CONTENT_TYPE') or ''
        if self.text_reg.search(content_type):
            log_cnt.write('body: {body}\n'.format(body=force_unicode(request.body)))
        post_data = ['{k}={v}'.format(k=k, v=v) for k, v in request.POST.items()]
        if post_data:
            log_cnt.write('post: {post}\n'.format(post='; '.join(post_data)))
        file_data = ['{k}={v}'.format(k=k, v=v) for k, v in request.FILES.items()]
        if file_data:
            log_cnt.write('files: {files}\n'.format(files='; '.join(file_data)))
        log_cnt.seek(0)
        self.logger.log(self.request_log_level, log_cnt.read())

    def process_view(self, request, callback, callback_args, callback_kwargs):
        """
        将view信息写入日志
        :param request:
        :param callback:
        :param callback_args:
        :param callback_kwargs:
        :return:
        """
        log_cnt = StringIO.StringIO()
        log_cnt.write('request [{rid}]: from {address} {method}\n'.format(
            rid=id(request),
            address=request.META['REMOTE_ADDR'],
            method=request.method
        ))
        module_name = callback.__module__
        if type(callback) is types.FunctionType:
            class_name = None
        elif type(getattr(callback, 'im_self')) is types.TypeType:
            class_name = callback.im_self.__name__
        elif type(getattr(callback, 'im_class')) is types.TypeType:
            class_name = callback.im_class.__name__
        else:
            class_name = None
        func_name = callback.__name__
        view = '.'.join([n for n in [module_name, class_name, func_name] if n])
        log_cnt.write('view: {view}\n'.format(view=view))
        log_cnt.seek(0)
        self.logger.log(self.request_log_level, log_cnt.read())

    def process_response(self, request, response):
        """
        将响应信息写入日志
        :param request:
        :param response:
        :return:
        """
        log_cnt = StringIO.StringIO()
        log_cnt.write('response for request [{rid}]: from {address} {method}\n'.format(
            rid=id(request),
            address=request.META['REMOTE_ADDR'],
            method=request.method
        ))
        headers = {}
        if isinstance(response, FileResponse):
            content = 'is a file'
        elif isinstance(response, HttpResponse):
            for k, v in response._headers.values():
                headers[k] = v
            if hasattr(response, 'render') and callable(response.render):
                response.render()
            content = response.content
            content_type = headers.get('Content-Type', 'text/html')
            if not self.json_reg.search(content_type) and len(content) > self.text_max_length:
                content = '{0} [{1}]; content too large.'.format(content_type, len(content))
        elif isinstance(response, (dict, list, tuple)):
            content = json.dumps(response)
        else:
            content = str(response)
        if headers:
            log_cnt.write('headers: {headers}\n'.format(
                headers='; '.join([ '{0}: {1}'.format(k, v) for k, v in headers.items()])
            ))
        if content:
            content = force_unicode(content)
            log_cnt.write('content: {content}\n'.format(content=content))
        log_cnt.seek(0)
        self.logger.log(self.response_log_level, log_cnt.read())
        return response


class ResponseMiddleware(object):
    """
    处理响应的中间件
    1 将标准错误转换为json响应
    2 在标准的json响应数据中加上status与msg
    """
    def __init__(self):
        self.setting = settings.MIDDLEWARE_CONFIG.get(self.__class__.__name__, {})
        self.status_param = self.setting.get('STATUS_PARAM', 'statusCode')
        self.msg_param = self.setting.get('MSG_PARAM', 'msg')
        self.data_param = self.setting.get('DATA_PARAM', 'data')
        self.ok_status = self.setting.get('OK_STATUS', 0)
        self.ok_msg = self.setting.get('OK_MSG', 'success')
        self.default_data_value = self.setting.get('DEFAULT_DATA', {})

    def process_exception(self, request, e):
        if not isinstance(e, StanderResponseError):
            return None
        return JsonResponse(
            OrderedDict([
                (self.status_param, e.status),
                (self.msg_param, _(e.msg)),
                (self.data_param, e.data if e.data else self.default_data_value)
            ])
        )

    def process_response(self, request, response):
        """
        对rest Response，dict，tuple，list及其子类进行返回结果包装
        :param request:
        :param response:
        :return:
        """
        status_code = self.ok_status
        msg = _('success')
        if isinstance(response, Response):
            data = response.data
            if response.exception:
                status_code = rest_error.status
                msg = rest_error.msg
                if isinstance(response.data, dict):
                    msg_list = []
                    for k, v in response.data.items():
                        v = self.str(v)
                        msg_list.append('{0}: {1}'.format(k, v))
                    msg = '; '.join(msg_list) or rest_error.msg
        elif isinstance(response, (dict, tuple, list)):
            data = response
        else:
            return response
        data = OrderedDict([
            (self.status_param, status_code),
            (self.msg_param, msg),
            (self.data_param, data)
        ])
        if isinstance(response, Response):
            response.data = data
            # 重新render
            response._is_rendered = False
            response = response.render()
            return response
        return Response(data)

    def str(self, obj):
        if isinstance(obj, (list, tuple)):
            return ', '.join([self.str(o) for o in obj])
        elif isinstance(obj, dict):
            return ', '.join(['{k}={v}'.format(k=k, v=self.str(v)) for k, v in obj.items()])
        else:
            return obj
