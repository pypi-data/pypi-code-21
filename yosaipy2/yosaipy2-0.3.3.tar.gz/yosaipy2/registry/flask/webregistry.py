#!/usr/bin/env python
# -*- coding: utf-8 -*-
from yosaipy2.web.registry.abcs import WebRegistry
from flask import request, g
from typing import Callable, Dict, Any
from werkzeug.exceptions import Forbidden, Unauthorized
import json


class FlaskWebRegistry(WebRegistry):
    def __init__(self):
        # type: (Callable[[Any], Dict]) -> None
        super(FlaskWebRegistry, self).__init__(request)

    def remote_host(self):
        return request.remote_addr

    def resource_params(self):
        # type: () -> Dict
        """
        Obtains the resource-specific parameters of the HTTP request, returning
        a dict that will be used to bind parameter values to dynamic permissions.
        """
        resource = dict()
        resource.update(request.values)
        if request.json is not None:
            resource.update(request.json)
        return resource

    def raise_forbidden(self, msg=None):
        """
        This method is called to raise HTTP Error Code 403 (Forbidden).
        """
        raise Forbidden(description=msg)

    def raise_unauthorized(self, msg=None):
        """
        This method is called to raise HTTP Error Code 401 (Unauthorized).
        """
        raise Unauthorized(description=msg)

    def _get_cookie(self, cookie_name, secret):
        if cookie_name in request.cookies:
            return request.cookies[cookie_name]
        return None

    def _set_cookie(self, response, cookie_name, cookie_val):
        response.set_cookie(
            key=cookie_name,
            value=cookie_val,
            max_age=self.set_cookie_attributes.get('cookie_max_age', None),
            path=self.set_cookie_attributes.get('cookie_path', '/'),
            domain=self.set_cookie_attributes.get('cookie_domain', None),
            secure=self.set_cookie_attributes.get('cookie_secure', None),
            httponly=self.set_cookie_attributes.get('cookie_httponly', False)
        )

    def _delete_cookie(self, response, cookie_name):
        response.set_cookie(cookie_name, '', expires=0)

    def register_response_callback(self):
        g.registry = self

    def __html__(self):
        data = {
            "secret": self.secret,
            "cookies": {
                'set_cookie': self.cookies['set_cookie'],
                'delete_cookie': list(self.cookies['delete_cookie']),
            },
            "session_creation_enabled": self._session_creation_enabled,
            "set_cookie_attributes": self.set_cookie_attributes,
        }
        return json.dumps(data)

    def decode(self, data):
        # type:(Dict) -> None
        self.secret = data['secret']
        self.cookies = {
            'set_cookie': data['cookies']['set_cookie'],
            'delete_cookie': set(data['cookies']['delete_cookie'])
        }
        self._session_creation_enabled = data['session_creation_enabled']
        self.set_cookie_attributes = data['set_cookie_attributes']
