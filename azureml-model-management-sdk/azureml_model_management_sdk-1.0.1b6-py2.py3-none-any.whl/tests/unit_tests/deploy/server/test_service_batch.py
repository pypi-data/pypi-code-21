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

from azureml.deploy.server import Service, Batch, EncodingType
from azureml.common import HttpClient, Configuration


class TestServiceBatch:

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
            'name': 'order',
            'version': 'v1',
            'description': 'Ordered arguments',
            'creationTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'outputFileNames': [],
            'operationId': 'transmission',
            'inputParameterDefinitions': [
                {'name': 'a', 'type': 'character'},
                {'name': 'b', 'type': 'character'},
                {'name': 'c', 'type': 'character'},
                {'name': 'd', 'type': 'character'},
                {'name': 'e', 'type': 'character'}
            ],
            'outputParameterDefinitions': [
                {
                    'name': 'answer',
                    'type': 'numeric'
                }
            ]
        }

    @pytest.fixture
    def service_beget(self):
        def factory(meta):
            return Service(meta, HttpClient(host=Configuration().host))

        return factory

    def test_service_object_batch_record_order(self, service_meta,
                                               service_beget):

        service = service_beget(service_meta)

        # 5 row values for col a,b,c,d,e
        records_col_order = pd.DataFrame({
            'a': ['a:row1', 'a:row2', 'a:row3', 'a:row4', 'a:row5'],
            'b': ['b:row1', 'b:row2', 'b:row3', 'b:row4', 'b:row5'],
            'c': ['c:row1', 'c:row2', 'c:row3', 'c:row4', 'c:row5'],
            'd': ['d:row1', 'd:row2', 'd:row3', 'd:row4', 'd:row5'],
            'e': ['e:row1', 'e:row2', 'e:row3', 'e:row4', 'e:row5']
        })[['b', 'a', 'd', 'e', 'c']]

        def print_records(label, before, after):
            print('---------------')
            print(label)
            print('---------------')
            print(before)
            print('---------------')
            for row in after:
                print(row)
            print('---------------')
            print(json.dumps(after[0]))
            print(json.dumps(after))
            print('---------------')

        batch_col = service.batch(records_col_order)
        ordered_col = batch_col.records

        # print_records('Column Order', records_col_order, ordered_col)

        service = service_beget(service_meta)

        # 5 row values for col a,b,c,d,e
        records_row_order = pd.DataFrame(
            [
                {"a": "a:row1", "b": "b:row1", "c": "c:row1", "d": "d:row1", "e": "e:row1"},
                {"a": "a:row2", "b": "b:row2", "c": "c:row2", "d": "d:row2", "e": "e:row2"},
                {"a": "a:row3", "b": "b:row3", "c": "c:row3", "d": "d:row3", "e": "e:row3"},
                {"a": "a:row4", "b": "b:row4", "c": "c:row4", "d": "d:row4", "e": "e:row4"},
                {"a": "a:row5", "b": "b:row5", "c": "c:row5", "d": "d:row5", "e": "e:row5"}
            ]
        )[['e', 'c', 'd', 'a', 'b']]

        batch_row = service.batch(records_row_order)
        ordered_row = batch_row.records

        # print_records('Column Order', records_col_order, ordered_col)

        assert ordered_col == ordered_row

    def test_service_object_batch_create(self, service_meta, service_beget):

        service = service_beget(service_meta)

        records = pd.DataFrame({
            'a': ['a:row1', 'a:row2', 'a:row3', 'a:row4', 'a:row5'],
            'b': ['b:row1', 'b:row2', 'b:row3', 'b:row4', 'b:row5'],
            'c': ['c:row1', 'c:row2', 'c:row3', 'c:row4', 'c:row5'],
            'd': ['d:row1', 'd:row2', 'd:row3', 'd:row4', 'd:row5'],
            'e': ['e:row1', 'e:row2', 'e:row3', 'e:row4', 'e:row5']
        })

        batch = service.batch(records)

        # 'Ensure successful `batch()` registration'
        assert isinstance(batch, Batch)

