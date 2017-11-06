# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest

from azureml.common.http_client import HttpClient
from azureml.common.configuration import Configuration

HOST = 'http://localhost:12800'
ACCESS_TOEKN = '123456789987654321-lmnop='


class TestHttpClient:
    
    @pytest.fixture
    def http_client(self):
        return HttpClient(host=HOST, access_token=ACCESS_TOEKN)
   
    def test_defualt_header_accept(self, http_client):
        assert http_client.accept == 'application/json'

    def test_defualt_header_content_type(self, http_client):
        assert http_client.content_type == 'application/json'

    @pytest.mark.parametrize(
        'name, value', [
            ('Content-Type', 'application/json'),
            ('Content-Type', 'application/xml'),            
            ('Accept', 'application/json'),
            ('Accept', 'text/plain, application/xml'),            
            ('x-header', 'x-header-value')            
        ])
    def test_setting_getting_headers(self, http_client, name, value):
        http_client.set_header(name, value)
        assert http_client.get_header(name) == value

    def test_authorization_header_with_default_prefix(self, http_client):        
        assert http_client.authorization == 'Bearer ' + ACCESS_TOEKN

    @pytest.mark.parametrize(
        'access_token', [
            ('new-access-token1'),
            ('new-access-token2'),
            ('new-access-token3')
        ])
    def test_setting_getting_authorization_header_with_default_prefix(self,  http_client, access_token):
        http_client.authorization = access_token
        assert http_client.authorization == 'Bearer ' + access_token

    @pytest.mark.parametrize(
        'prefix', [
            ('prefix1'),
            ('prefix2'),
            ('prefix3')
        ])
    def test_setting_setting_authorization_header_with_new_prefix(self,
                                                                  http_client,
                                                                  prefix):
        Configuration().api_key_prefix = prefix
        http_client.authorization = ACCESS_TOEKN
        assert http_client.authorization == prefix + ' ' + ACCESS_TOEKN        
