# Copyright 2016 Internap.
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

import ubersmith_client
from mock import Mock, patch
from hamcrest import assert_that, raises, calling, equal_to
from requests.exceptions import ConnectionError, Timeout

from ubersmith_client import exceptions
from ubersmith_client.ubersmith_request import UbersmithRequest

from tests.ubersmith_json.response_data_structure import a_response_data


class UbersmithRequestTest(unittest.TestCase):
    def setUp(self):
        self.url = 'http://ubersmith.example.com/'
        self.username = 'admin'
        self.password = 'test'

    def test_process_ubersmith_response(self):
        response = Mock(status_code=200, headers={'content-type': 'application/json'})

        json_data = {
            'client_id': '1',
            'first': 'Rick',
            'last': 'Sanchez',
            'company': 'Wubba lubba dub dub!'
        }

        response.json = Mock(return_value=a_response_data(data=json_data))

        self.assertDictEqual(json_data, UbersmithRequest.process_ubersmith_response(response))

    def test_process_ubersmith_response_not_application_json(self):
        response = Mock(status_code=200, headers={'content-type': 'text/html'}, content='42')
        assert_that(response.content, equal_to(UbersmithRequest.process_ubersmith_response(response)))

    def test_process_ubersmith_response_raise_exception(self):
        response = Mock(status_code=400, headers={'content-type': 'application/json'})
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.BadRequest))

        response.status_code = 401
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.Unauthorized))

        response.status_code = 403
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.Forbidden))

        response.status_code = 404
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.NotFound))

        response.status_code = 500
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.UnknownError))

        response.status_code = 200
        response.json = Mock(return_value={'status': False, 'error_code': 42, 'error_message': 'come and watch tv'})
        assert_that(calling(UbersmithRequest.process_ubersmith_response).with_args(response),
                    raises(exceptions.UbersmithException, 'Error code 42 - message: come and watch tv'))

    @patch('ubersmith_client.ubersmith_request_post.requests')
    def test_api_method_returns_handle_connection_error_exception(self, requests_mock):
        ubersmith_api = ubersmith_client.api.init(self.url, self.username, self.password)
        requests_mock.post = Mock(side_effect=ConnectionError())

        assert_that(calling(ubersmith_api.client.list), raises(exceptions.UbersmithConnectionError))

    @patch('ubersmith_client.ubersmith_request_post.requests')
    def test_api_method_returns_handle_timeout_exception(self, requests_mock):
        ubersmith_api = ubersmith_client.api.init(self.url, self.username, self.password)
        requests_mock.post = Mock(side_effect=Timeout())

        assert_that(calling(ubersmith_api.client.list), raises(exceptions.UbersmithTimeout))
