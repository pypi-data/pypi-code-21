# -*- coding: utf-8 -*-

"""
Copyright 2017 Axibase Corporation or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License").
You may not use this file except in compliance with the License.
A copy of the License is located at

https://www.axibase.com/atsd/axibase-apache-2.0.pdf

or in the "license" file accompanying this file. This file is distributed
on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
express or implied. See the License for the specific language governing
permissions and limitations under the License.
"""
import logging

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import requests
from . import _jsonutil

from .exceptions import ServerException

from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

logging.basicConfig(level=logging.INFO)


class Client(object):
    """
    low level request wrapper
    sets method, path, payload
    returns response data
        or True if request was successful without content
    """

    def __init__(self, base_url,
                 username=None, password=None,
                 ssl_verify=False, timeout=None):
        """
        :param base_url: atsd url
        :param username: login
        :param password:
        :param ssl_verify: verify ssl certificate
        :param timeout: request timeout
        """
        logging.info('Connecting to ATSD at %s as %s user.' % (base_url, username))
        self.context = urlparse.urljoin(base_url, 'api/')
        session = requests.Session()
        if ssl_verify is False or ssl_verify == 'False':
            session.verify = False
        if username is not None and password is not None:
            session.auth = (username, password)
        self.session = session
        self.timeout = int(timeout) if timeout is not None else None

    def _request(self, method, path, params=None, json=None, data=None):
        request = requests.Request(
            method=method,
            url=urlparse.urljoin(self.context, path),
            data=data,
            json=_jsonutil.serialize(json),
            params=params
        )
        prepared_request = self.session.prepare_request(request)
        response = self.session.send(prepared_request, timeout=self.timeout)
        if response.status_code is not 200:
            raise ServerException(response.status_code, response.text)
        try:
            return response.json()
        except ValueError:
            return response.text

    def post(self, path, data, params=None):
        return self._request('POST', path, params=params, json=data)

    def post_plain_text(self, path, data, params=None):
        return self._request('POST', path, params=params, data=data)

    def patch(self, path, data):
        return self._request('PATCH', path, json=data)

    def get(self, path, params=None):
        return self._request('GET', path, params=params)

    def put(self, path, data):
        return self._request('PUT', path, json=data)

    def delete(self, path):
        return self._request('DELETE', path)
