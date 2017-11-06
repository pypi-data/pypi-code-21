# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest
import requests_mock
import numpy as np
import pandas as pd
import json

from azureml.deploy.server import Service, ServiceResponse, EncodingType
from azureml.common import HttpClient, Configuration


class TestService:

    @pytest.fixture
    def adapter(self):
        def factory(resource, method, json=None, status_code=None):

            url = Configuration().host + resource
            adapter = requests_mock.Adapter()

            if json is not None:
                adapter.register_uri(method, url, json=json)
            else:
                adapter.register_uri(method, url, status_code=status_code)

            http_client = HttpClient(host=Configuration().host)
            http_client.mount(url, adapter)

            return http_client

        return factory

    @pytest.fixture
    def service_meta(self):
        return {
            'name': 'transmission',
            'version': 'v1',
            'description': 'Support the transmission...',
            'creationTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'outputFileNames': ['file1.png', 'file2.png'],
            'operationId': 'transmission',
            'inputParameterDefinitions': [
                {
                    'name': 'hp',
                    'type': 'numeric'
                },
                {
                    'name': 'wt',
                    'type': 'numeric'
                }
            ],
            'outputParameterDefinitions': [
                {
                    'name': 'answer',
                    'type': 'numeric'
                }
            ]
        }

    @pytest.fixture
    def raw_response(self):
        out_int = 5
        out_float = 4.567
        out_str = 'MLServer'
        out_bool = True
        out_nparray = [1, 2, 3]
        out_npmatrix = [[1, 2], [3, 4]]  # np.matrix([[1, 2], [3, 4]])
        out_df = {
            'n': [2.0, 3.0, 5.0],
            's': ['aa', 'bb', 'cc'],
            'b': [True, False, True]
        }

        output_schema = [
            {'name': 'out_int', 'type': EncodingType.integer.value},
            {'name': 'out_float', 'type': EncodingType.numeric.value},
            {'name': 'out_str', 'type': EncodingType.character.value},
            {'name': 'out_bool', 'type': EncodingType.logical.value},
            {'name': 'out_numpy.array', 'type': EncodingType.vector.value},
            {'name': 'out_numpy.matrix', 'type': EncodingType.matrix.value},
            {'name': 'out_pandas.DataFrame',
             'type': EncodingType.dataframe.value}
        ]

        raw_response = {
            'outputs': {},
            'response': {
                'success': True,
                'errorMessage': "NameError: name 'p' is not defined",
                'consoleOutput': "{'a': 5}",
                'changedFiles': ['file1.png', 'file2.png'],
                'outputParameters': {
                    'out_int': out_int,
                    'out_float': out_float,
                    'out_str': out_str,
                    'out_bool': out_bool,
                    'out_numpy.array': out_nparray,
                    'out_numpy.matrix': out_npmatrix,
                    'out_pandas.DataFrame': out_df
                },
                'outputFiles': {
                    'file1.png': 'base64StrImage',
                    'file2.png': 'base64StrImage'
                }
            }
        }

        raw_response['outputs'] = output_schema

        return raw_response

    @pytest.fixture
    def service_beget(self):
        def factory(meta):
            return Service(meta, HttpClient(host=Configuration().host))

        return factory

    def test_service_object_swagger_as_dict(self, service_meta, adapter):
        name = service_meta['name']
        version = service_meta['version']
        api = '/api/' + name + '/' + version + '/swagger.json'
        response = {
            "swagger": "2.0",
            "info": {
                "version": version,
                "title": name,
                "license": {
                    "name": "MIT"
                }
            },
            "host": Configuration().host,
            "basePath": "/api"
        }

        # mock request adapter for this service swagger
        http_client = adapter(api, 'GET', json=response)
        service = Service(service_meta, http_client)

        swagger = service.swagger()

        assert json.dumps(response) == swagger

    def test_service_object_capabilities(self, service_meta, service_beget):
        service = service_beget(service_meta)
        cap = service.capabilities()
        host = Configuration().host
        api = service_meta.get('name') + '/' + service_meta.get('version')
        swagger = host + '/api/' + api + '/swagger.json'

        assert cap.get('name') == service_meta.get('name')
        assert cap.get('version') == service_meta.get('version')
        assert cap.get('description') == service_meta.get('description')
        assert cap.get('creation_time') == service_meta.get('creationTime')
        assert cap.get('snapshot_id') == service_meta.get('snapshotId')
        assert cap.get('inputs') == service_meta.get('inputParameterDefinitions')
        assert cap.get('outputs') == \
            service_meta.get('outputParameterDefinitions')
        assert cap.get('artifacts') == service_meta.get('outputFileNames')
        assert cap.get('alias') == service_meta.get('alias')
        assert cap.get('swagger') == swagger

    def test_service_object_alias_fn_is_callable(self, service_meta, adapter):
        api = '/api/' + service_meta['name'] + '/' + service_meta['version']
        response = {
            'success': True,
            'errorMessage': '',
            'consoleOutput': '',
            'changedFiles': [],
            'outputParameters': {
                'answer': 0.64181
            }
        }

        # mock request adapter for this service API call
        http_client = adapter(api, 'POST', json=response)
        service = Service(service_meta, http_client)

        # service invocation
        res = service.transmission(120, 2.8)

        assert res.output('answer') == response['outputParameters']['answer']

    def test_service_object_creation(self, service_meta, service_beget):
        service = service_beget(service_meta)
        expected_name = 'TransmissionService'

        assert service.__class__.__name__ == expected_name

    @pytest.mark.parametrize(
        'name, class_name', [
            ('test', 'TestService'),
            ('12345', 'Service12345Service'),
            ('a!b@c#d$e%f^g&h*i(j)k-l+m.n,o<p_alphanumeric',
             'ABCDEFGHIJKLMNOPAlphanumericService')
        ])
    def test_service_object_class_name(self,
                                       name,
                                       class_name,
                                       service_meta,
                                       service_beget):

        service_meta['name'] = name
        service = service_beget(service_meta)

        assert service.__class__.__name__ == class_name

    def test_service_object_alias_creation(self, service_meta, service_beget):
        service = service_beget(service_meta)
        expected_name = service_meta['operationId']  # operationId == alias

        fn = getattr(service, expected_name, None)
        assert fn is not None and callable(fn)

    def test_service_response_object_creation(self, raw_response):
        name = 'TestService'
        version = 'v1'
        api = '/api/' + name + '/' + version
        outputs = raw_response.get('outputs')
        response = raw_response.get('response')

        sr = ServiceResponse(api, response, outputs)

        assert sr.error == response['errorMessage']
        assert sr.console_output == response['consoleOutput']

        # -- expected values --
        expected = response.get('outputParameters')

        # by `outputs[name]` dict
        assert sr.outputs['out_int'] == expected.get('out_int')
        assert sr.outputs['out_float'] == expected.get('out_float')
        assert sr.outputs['out_str'] == expected.get('out_str')
        assert sr.outputs['out_bool'] == expected.get('out_bool')
        assert np.all(sr.outputs['out_numpy.array'] ==
                      np.array(expected.get('out_numpy.array')))
        assert np.all(sr.outputs['out_numpy.matrix'] ==
                      np.matrix(expected.get('out_numpy.matrix')))
        assert np.all(sr.outputs['out_pandas.DataFrame'] ==
                      pd.DataFrame(expected.get('out_pandas.DataFrame')))
        # by `output(name)` fn
        assert sr.output('out_int') == expected.get('out_int')
        assert sr.output('out_float') == expected.get('out_float')
        assert sr.output('out_str') == expected.get('out_str')
        assert sr.output('out_bool') == expected.get('out_bool')
        assert np.all(sr.output('out_numpy.array') ==
                      np.array(expected.get('out_numpy.array')))
        assert np.all(sr.output('out_numpy.matrix') ==
                      np.matrix(expected.get('out_numpy.matrix')))
        assert np.all(sr.output('out_pandas.DataFrame') ==
                      pd.DataFrame(expected.get('out_pandas.DataFrame')))
