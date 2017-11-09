# Copyright 2017 Internap.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from abc import abstractmethod
from requests import Timeout, ConnectionError

from ubersmith_client import exceptions


class UbersmithRequest(object):
    def __init__(self, url, user, password, module, timeout):
        self.url = url
        self.user = user
        self.password = password
        self.module = module
        self.methods = []
        self.timeout = timeout

    def __getattr__(self, function):
        self.methods.append(function)
        return self

    @abstractmethod
    def __call__(self, **kwargs):
        raise AttributeError

    def _process_request(self, method, **kwargs):
        try:
            return method(**kwargs)
        except ConnectionError:
            raise exceptions.UbersmithConnectionError(self.url)
        except Timeout:
            raise exceptions.UbersmithTimeout(self.url, self.timeout)

    def _build_request_params(self, kwargs):
        _methods = '.'.join(self.methods)
        kwargs['method'] = '{0}.{1}'.format(self.module, _methods)

    @staticmethod
    def process_ubersmith_response(response):
        if response.status_code < 200 or response.status_code >= 400:
            raise exceptions.get_exception_for(status_code=response.status_code)

        if response.headers['content-type'] == 'application/json':
            response_json = response.json()
            if not response_json['status']:
                raise exceptions.UbersmithException(response_json['error_code'],
                                                    response_json['error_message'])
            return response_json['data']

        return response.content
