#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
author lilx
created on 2016/8/4
 """
from __future__ import unicode_literals, absolute_import
from django.conf import settings
from django.utils.encoding import force_unicode
from djdg_core.utils.hailstone import regular_url
from djdg_core.exceptions import StanderResponseError
from djdg_oauth.oauthcore import getSign
import requests
from requests.models import complexjson
from requests_toolbelt import MultipartEncoder


class RestClient(object):
    """
    restful 接口调用客户端
    """
    default_headers = (
        ('Content-Type', 'application/json;charset=utf-8'),
    )

    def __init__(self,
                 host,
                 base_url='/',
                 protocol='http',
                 headers=None,
                 logger=None,
                 oauth_app_id=None,
                 oauth_app_secret=None
                 ):
        self.host = regular_url(host)
        self.base_url = regular_url(base_url)
        self.protocol = protocol
        headers = headers if headers else ()
        self.__headers = headers + self.default_headers
        self.logger = logger
        self.oauth_app_id = oauth_app_id
        self.oauth_app_secret = oauth_app_secret

    def get_headers(self):
        d = {}
        for k, v in self.__headers:
            d[k] = v
        return d

    def get_resource(self, name, app=None, token=None):
        path = regular_url(name)
        if app:
            path = '{0}{1}'.format(regular_url(app), path)
        url = '{protocol}://{host}{base_url}{path}'.format(
            protocol=self.protocol,
            base_url=self.base_url,
            host=self.host,
            path=path
        )
        return RestResource(url, self, token)


class RestResource(object):
    """
    restful 资源
    """
    methods = ('get', 'post', 'put', 'delete', 'options', 'head', 'patch')

    def __init__(self, url, client, token=None):
        self.url = url
        self.client = client
        self.token = token
        self.logger = getattr(client, 'logger')

    def do_request(self, method, action=None, data=None, params=None, headers=None, json=None, raise_exception=True,
                   end_slash=True, multi_part_fields=None):
        send_headers = self.client.get_headers()
        if self.token:
            send_headers['token'] = self.token
        if headers:
            send_headers.update(headers)
        if self.client.oauth_app_id is not None and self.client.oauth_app_secret is not None:
            # 认证中间件先检查有误Authorization，后检查有无token
            # send_headers.pop('token', None)
            if 'get' == method:
                params = params if params else {}
                params['appid'] = self.client.oauth_app_id
                sign_body = params
                send_headers.pop('Content-Type', None)
            elif multi_part_fields:
                m = MultipartEncoder(fields=multi_part_fields)
                data = m.to_string()
                send_headers['Content-Type'] = m.content_type
                sign_body = data
            else:
                json = json if json else {}
                json['appid'] = self.client.oauth_app_id
                data = complexjson.dumps(json)
                sign_body = data
            send_headers['Authorization'] = getSign(sign_body, self.client.oauth_app_secret)
            send_headers['appid'] = self.client.oauth_app_id
        if action:
            action = regular_url(action)
            url = '{0}{1}'.format(self.url, action)
        else:
            url = self.url
        if not end_slash:
            url = url.rstrip('/')
        res = requests.request(method, url, data=data, params=params, headers=send_headers, json=json)
        ret = Result(res)
        if self.logger:
            content_type = send_headers.get('Content-Type') or ''
            content_type = content_type.lower()
            if content_type.startswith('multipart'):
                body = content_type
            else:
                body = force_unicode(res.request.body) if res.request.body is not None else None
            msg = 'request {uri} {method} {status_code} \nheaders: {headers}\nbody: {body}\nresponse: {resp}'.format(
                uri=res.request.url,
                method=res.request.method,
                status_code=res.status_code,
                headers='; '.join(['{k}: {v}'.format(k=k, v=v) for k, v in send_headers.items()]),
                body=body,
                resp=force_unicode(res.content)
            )
            self.logger.info(msg)
        if raise_exception and ret.status != settings.RESPONSE_CONFIG['OK_STATUS']:
            raise StanderResponseError(ret.status, ret.msg, getattr(ret, 'data', {}))
        return ret

    def __getattr__(self, item):
        method = item.lower()
        action = None
        if method not in self.methods:
            for m in self.methods:
                if method.startswith(m):
                    method = m
                    action = item[len(m) + 1:]
                    break
            else:
                action = item
        return Method(self, method, action)


class Method(object):
    """
    模拟请求
    """
    def __init__(self, resource, method=None, action=None):
        self.resource = resource
        self.method = method
        self.action = action
        self.token = None

    def __call__(self, data=None, params=None, method=None, headers=None, action_to=None, raise_exception=True,
                 end_slash=True, multi_part_fields=None, **kwargs):
        if method:
            self.method = method
        if not self.method:
            self.method = 'post' if data else 'get'
        if 'get' == self.method:
            params = params if params else {}
            params.update(kwargs)
        else:
            data = data if data else {}
            data.update(kwargs)
        action = ''
        if action_to:
            action = '{0}/'.format(action_to)
        if self.action:
            action = '{0}{1}/'.format(action, self.action)
        headers = headers if headers else {}
        if self.token:
            headers['token'] = self.token
        return self.resource.do_request(self.method,
                                        action=action,
                                        json=data,
                                        params=params,
                                        headers=headers,
                                        raise_exception=raise_exception,
                                        end_slash=end_slash,
                                        multi_part_fields=multi_part_fields
                                        )

    def __getattr__(self, item):
        method = item.lower()
        if method not in self.resource.methods:
            for m in self.resource.methods:
                if method.startswith(m):
                    self.method = m
                    self.action = item[len(m) + 1:]
                    break
            else:
                self.action = item
        else:
            self.method = method
        return self

    def set_token(self, token):
        self.token = token
        return self


class Result(object):
    """
    restful 响应数据
    """
    def __init__(self, response):
        self.__resp = response
        self.__data = None
        self.__result = None

    @property
    def result(self):
        if self.__result is None:
            if 500 == self.status_code:
                self.__result = {
                    settings.RESPONSE_CONFIG['MSG_PARAM']: self.__resp.text,
                    settings.RESPONSE_CONFIG['DATA_PARAM']: {},
                    settings.RESPONSE_CONFIG['STATUS_PARAM']: self.status_code
                }
            else:
                try:
                    self.__result = self.__resp.json()
                except Exception as e:
                    raise StanderResponseError(2, e.message)
        return self.__result

    @property
    def data(self):
        return self.result.get(settings.RESPONSE_CONFIG['DATA_PARAM'], None)

    def __getattr__(self, item):
        return self.result[item]

    @property
    def status(self):
        return self.result[settings.RESPONSE_CONFIG['STATUS_PARAM']]

    @property
    def status_code(self):
        return self.__resp.status_code
