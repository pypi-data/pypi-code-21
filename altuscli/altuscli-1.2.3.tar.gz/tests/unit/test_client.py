# Copyright 2012-2013 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Modifications made by Cloudera are:
#     Copyright (c) 2016 Cloudera, Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import os

from altuscli.client import ClientCreator
from altuscli.exceptions import ClientError
from altuscli.exceptions import OperationNotPageableError
from altuscli.exceptions import ParamValidationError
from altuscli.parser import ResponseParserFactory
from mock import Mock
from tests import unittest
import yaml

USE_DEFAULT_ENDPOINT_URL = None
VERIFY_TLS = True
CLIENT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'client')


class TestClient(unittest.TestCase):

    def setUp(self):
        self.loader = Mock()
        self.loader.load_service_data.return_value = yaml.load(
            open(os.path.join(CLIENT_DIR, 'service.yaml')))
        self.endpoint = Mock()
        self.endpoint.host = 'http://thunderhead.cloudera.altus.cloudera.com'
        self.endpoint.make_request.return_value = (Mock(status_code=200), {})

        self.endpoint_creator = Mock()
        self.endpoint_creator.create_endpoint.return_value = self.endpoint
        self.retryhandler = Mock()
        self.client_creator = ClientCreator(self.loader,
                                            self.endpoint_creator,
                                            'user-agent-header',
                                            ResponseParserFactory(),
                                            self.retryhandler)
        self.credentials = Mock()

    def _create_client(self):
        return self.client_creator.create_client(
            'thunderhead', USE_DEFAULT_ENDPOINT_URL, VERIFY_TLS, self.credentials)

    def _get_request_params(self):
        self.assertTrue(self.endpoint.make_request.called)
        return dict((k.lower(), v) for k, v in
                    self.endpoint.make_request.call_args[0][1].items())

    def test_client_name(self):
        client = self._create_client()
        self.assertEquals(client.__class__.__name__, 'thunderhead')

    def test_client_meta(self):
        client = self._create_client()
        self.assertTrue(client.meta is not None)
        self.assertTrue(client.meta.service_model is not None)
        self.assertEquals(client.meta.endpoint_url,
                          'http://thunderhead.cloudera.altus.cloudera.com')

    def test_client_operations(self):
        client = self._create_client()
        self.assertTrue(hasattr(client, 'create_director'))
        self.assertFalse(hasattr(client, 'non_existent_operation'))

    def test_client_method_to_api_mapping(self):
        client = self._create_client()
        self.assertEqual(client.meta.method_to_api_mapping['create_director'],
                         'createDirector')

    def test_client_call(self):
        client = self._create_client()
        response = client.describe_directors()
        self.assertTrue(self.endpoint.make_request.called)
        self.assertEqual(response, {})

    def test_get_paginator(self):
        client = self._create_client()
        self.assertTrue(client.get_paginator('describe_directors') is not None)
        with self.assertRaises(OperationNotPageableError):
            client.get_paginator('create_director')

    def test_client_user_agent_in_request(self):
        client = self._create_client()
        client.describe_directors()
        self.assertTrue(self.endpoint.make_request.called)
        params = self._get_request_params()
        self.assertEqual(params['headers']['User-Agent'], 'user-agent-header')

    def test_client_error_message_for_positional_args(self):
        client = self._create_client()
        with self.assertRaisesRegexp(TypeError, 'only accepts keyword arguments'):
            client.create_director('foo')

    def test_client_error(self):
        client = self._create_client()
        error = {'error': {'code': 'test-code', 'message': 'test-message'}}
        mock_response = Mock(
            status_code=400,
            headers={'x-altus-request-id': '00000000-0000-0000-0000-000000000000'})
        self.endpoint.make_request.return_value = (mock_response, error)
        re = (
            'An error occurred: test-message '
            '\(Status Code: 400; '
            'Error Code: test-code; '
            'Service: thunderhead; '
            'Operation: describeDirectors; '
            'Request ID: 00000000-0000-0000-0000-000000000000;\)')
        with self.assertRaisesRegexp(ClientError, re) as e:
            client.describe_directors()
        self.assertEqual(e.exception.response['error']['code'], 'test-code')
        self.assertEqual(e.exception.response['error']['message'], 'test-message')

    def test_client_validates_params(self):
        client = self._create_client()
        with self.assertRaises(ParamValidationError):
            client.create_director()

    def test_operation_cannot_paginate(self):
        client = self._create_client()
        self.assertTrue(hasattr(client, 'create_director'))
        self.assertFalse(client.can_paginate('create_director'))

    def test_operation_can_paginate(self):
        client = self._create_client()
        self.assertTrue(hasattr(client, 'describe_directors'))
        self.assertTrue(client.can_paginate('describe_directors'))
