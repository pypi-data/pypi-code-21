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

import unittest

from mock import sentinel, patch, MagicMock

from ubersmith_client.ubersmith_request_get import UbersmithRequestGet
from ubersmith_client.ubersmith_request_post import UbersmithRequestPost


class UbersmithRequestFormEncodingTest(unittest.TestCase):
    def setUp(self):
        self.ubersmith_constructor_params = (sentinel.url, sentinel.username, sentinel.password,
                                             sentinel.module, sentinel.timeout)
        self._standard_kwargs = dict(auth=(sentinel.username, sentinel.password),
                                     timeout=sentinel.timeout,
                                     url=sentinel.url,
                                     headers={'user-agent': 'python-ubersmithclient'})

    @patch('ubersmith_client.ubersmith_request_get.requests')
    def test_get_with_list(self, request_mock):
        request_mock.get.return_value = MagicMock(status_code=200)

        self.client = UbersmithRequestGet(*self.ubersmith_constructor_params)
        self.client.call(test=['a'])

        expected_args = self._standard_kwargs
        expected_args.update(dict(params={
            'method': 'sentinel.module.call',
            'test[0]': 'a',
        }))
        request_mock.get.assert_called_with(**expected_args)

    @patch('ubersmith_client.ubersmith_request_post.requests')
    def test_post_with_list(self, request_mock):
        request_mock.post.return_value = MagicMock(status_code=200)

        self.client = UbersmithRequestPost(*self.ubersmith_constructor_params)
        self.client.call(test=['a'])

        expected_args = self._standard_kwargs
        expected_args.update(dict(data={
            'method': 'sentinel.module.call',
            'test[0]': 'a',
        }))
        request_mock.post.assert_called_with(**expected_args)
