#
# Copyright 2014 Mortar Data Inc.
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
#

import unittest2 as unittest

from mortar.api.v2 import gateways

from requests.exceptions import HTTPError

import mock

class TestClusters(unittest.TestCase):

    def setUp(self):
        self.api_mock = mock.Mock()
    
    def test_get_gateway_active(self):
        response = {
            "gateway_id": "54h35ce326fdc53fds6ef7320",
            "status_code": "running",
            "start_timestamp": "2014-09-26T12:32:38.933000+00:00",
            "private_address": "ip-10-121-130-134.ec2.internal",
            "public_address": "ec2-54-194-211-224.compute-1.amazonaws.com"
        }
        self.api_mock.get.return_value = response
        return_gateway = gateways.get_gateway(self.api_mock)
        self.assertEquals(return_gateway, response)

    def test_get_gateway_not_active(self):
        response_mock_404 = mock.Mock()
        response_mock_404.status_code = 404
        response_mock_404.reason = 'Not Found'
        response_mock_404.text = 'The resource could not be found.'
        self.api_mock.get.side_effect = HTTPError('Message', response=response_mock_404)
        return_gateway = gateways.get_gateway(self.api_mock)
        self.assertIsNone(return_gateway)
