# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest
import requests_mock
import os
from azureml.deploy.server.mlserver import MLServer
from azureml.common import HttpClient, Configuration
import pickle
#from .utils import services_resource

HOST = 'http://localhost:12800'
ACCESS_TOKEN = '123456789987654321-lmnop='
WS_PATCH_TARGET = 'azureml.deploy.server.services.WebServiceService'


def services_resource(name=None, version=None):
    resource = '/services'

    if name is not None:
        resource += '/' + name

    if version is not None:
        resource += '/' + version

    return Configuration().host + resource


class TestMLServer:

    @pytest.fixture
    def service_meta(self):
        return {
            'name': 'transmission',
            'version': 'v1',
            'description': 'Support the transmission...',
            'creationTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'outputFileNames': ['file1.png', 'file2.png'],
            'inputParameterDefinitions': [
                {'name': 'hp', 'type': 'numeric'},
                {'name': 'wt', 'type': 'numeric'}
            ],
            'outputParameterDefinitions': [
                {'name': 'answer', 'type': 'numeric'}
            ],
            'operationId': 'transmission'
        }

    @pytest.fixture
    def realtime_meta(self):
        return {
            'name': 'transmission',
            'version': 'v1',
            'description': 'Realtime Service...',
            'creationTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'inputParameterDefinitions': [
                {
                    'name': 'intData',
                    'type': 'dataframe'
                }
            ],
            'outputParameterDefinitions': [
                {
                    'name': 'outputData',
                    'type': 'dataframe'
                }
            ],
            'operationId': 'transmission'
        }

    @pytest.fixture
    def client(self):
        config = Configuration()
        http_client = HttpClient(host=config.host)
        mls = MLServer()            
        mls.initializer(http_client, config)
        return mls

    @pytest.fixture
    def client_adapters(self):
        def factory(adapters):            
            config = Configuration()
            http_client = HttpClient(host=config.host)
            mls = MLServer()            
            mls.initializer(http_client, config, adapters=adapters)
            return mls

        return factory    

    @pytest.fixture
    def adapter(self):
        def factory(resource, method, json=None, status_code=None):
            url = Configuration().host + resource
            adapter = requests_mock.Adapter()

            if json is not None:
                adapter.register_uri(method, url, json=json)
            else:
                adapter.register_uri(method, url, status_code=status_code)

            #  adapter.register_uri(method, url, json=json)

            return adapter

        return factory
    
    def test_ad_authentication(self, adapter):
        config = Configuration()
        http_client = HttpClient(host=config.host)

        response = {'access_token': ACCESS_TOKEN}
        adapters = adapter('/login', 'POST', json=response)
        
        mls = MLServer()
        mls.initializer(http_client, config, adapters=adapters)
        
        context = ('USERNAME', 'PASSWORD')
        mls.authentication(context)
        
        expected = Configuration().api_key_prefix + ' ' + ACCESS_TOKEN
        assert mls._http_client.authorization == expected
        
    @pytest.mark.parametrize(
        'patch, version', [
            ('get_service', 'v1'),
            ('get_latest_service', None)
        ])
    def test_get_service(self, mocker, client, service_meta, patch, version):
        mock = mocker.patch(WS_PATCH_TARGET + '.' + patch)
        mock.return_value = service_meta

        service = client.get_service(service_meta['name'], version=version)
        cap = service.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    @pytest.mark.parametrize(
        'patch, name, version, response', [
            ('get_service', 'foo-service', 'v1',
             {'name': 'foo-service', 'version': 'v1'}
            ),
            ('get_service', 'foo-service', 'v1', []),
            ('get_service_versions', 'baz-service', None, [
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'}
            ]),
            ('get_service_versions', 'foo-service', None, []),
            ('get_all_services', None, None, [
                {'name': 'foo-service', 'version': 'v1'},
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'}
             ]),
            ('get_all_services', None, None, []),
        ])
    def test_list_services(self, mocker, client, patch, name, version, response):                
        mock = mocker.patch(WS_PATCH_TARGET + '.' + patch)
        mock.return_value = response
        service = client.list_services(name=name, version=version)

        if not isinstance(response, list):
            response = [response]

        assert service == response
    
    @pytest.mark.parametrize(
        'name, version, response', [
            ('foo-service', 'v1', True),
            ('bar-service', 'v2', True)            
        ])
    def test_delete_service(self, mocker, client, name, version, response):  
        mock = mocker.patch(WS_PATCH_TARGET + '.delete_service')
        mock.return_value = response
        status = client.delete_service(name, version=version)
        #raise ValueError('Missing the required parameter `version`')

        assert status == True
    
    def test_delete_service_no_version_error(self, client):  
        
        with pytest.raises(ValueError) as excinfo:
            client.delete_service('valid-service')
        
        excinfo.match('Missing the required parameter `version`')

    @pytest.mark.parametrize('version', ['v1', None])
    def test_deploy_service(self, mocker, client, service_meta, version):
        mock = mocker.patch(WS_PATCH_TARGET + '.create_service')
        mock.return_value = service_meta
        
        # -- patch get_*_service as well because it is called internally  --
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = service_meta
        mock = mocker.patch(WS_PATCH_TARGET + '.get_latest_service')
        mock.return_value = service_meta
        
        # --- Publish service via `kwargs` dictionary ---
        def add_one(x):
            return x + 1

        def init():
            print('init add-one service')

        model = 5
        local_obj = 'hello'
        kwargs = {
            'version': version,
            'code_fn': add_one,
            'init_fn': init,
            'objects': {'local_obj': local_obj},
            'models': {'model': model},
            'inputs': {'hp': float, 'wt': float},
            'outputs': {'answer': float},
            'artifacts': service_meta['outputFileNames'],
            'description': service_meta['description']
        }
                        
        service = client.deploy_service(service_meta['name'], **kwargs)

        cap = service.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    @pytest.mark.parametrize(
        'version', ['v1', None]
    )
    def test_deploy_realtime(self, mocker, client, version, realtime_meta):
        mock = mocker.patch(WS_PATCH_TARGET + '.create_realtime')
        mock.return_value = realtime_meta

        # -- patch get_*_service as well because it is called internally  --
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = realtime_meta
        mock = mocker.patch(WS_PATCH_TARGET + '.get_latest_service')
        mock.return_value = realtime_meta

        # -- serialize fake model
        model = 'the_model'
        s_model = pickle.dumps(model)
        # --- Publish service via `kwargs` dictionary ---
        kwargs = {
            'version': version,
            'serialized_model': s_model,
            'description': 'The Description of the `add-one` service'
        }

        service = client.deploy_realtime(realtime_meta["name"], **kwargs)
        cap = service.capabilities()
        assert cap['name'] == realtime_meta["name"]
        assert cap['version'] == realtime_meta["version"]

    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #
    # ------------------------------------------------------------------------ #

    # --------------------------------------------------------------------------
    # Lower-level tests mocking the mounted request `adapters` used.
    #
    # This exercises the module in its entirety with the exception of the http
    # request/response. Basically a http reponse is the only mocked attribute
    # which gets us closer to the full-path.
    # --------------------------------------------------------------------------

    def test_deploy_service_with_adapters(self, client_adapters, adapter,
                                          service_meta):
        client = client_adapters
        name = service_meta['name']
        version = service_meta['version']
        host = Configuration().host
        adapters = []

        session_id = 'session-id-123456'
        snapshot_id = service_meta['snapshotId']

        # --- Or Publish service via `kwargs` dictionary ---
        def add_one(x):
            return x + 1

        def init():
            print('init add-one service')

        model = 5
        local_obj = 'hello'        
        kwargs = { 
            'version': version, 
            'code_fn': add_one,
            'init_fn': init,
            'objects': {'local_obj': local_obj},
            'models': {'model': model},
            'inputs': {'x': int},
            'outputs': {'answer': float},
            'artifacts': service_meta['outputFileNames'],
            'description': service_meta['description']
        }

        # 1. - Create session: POST /sessions
        url = '/sessions'
        res = {'sessionId': session_id}
        adapters.append((host + url, adapter(url, 'POST', json=res)))

        # 2. - Add object(s): POST /sessions/:id/workspace/:object-name
        url = '/sessions/' + session_id + '/workspace/local_obj'
        adapters.append((host + url, adapter(url, 'POST', status_code=200)))

        # 2.1 - Add object(s): POST /sessions/:id/workspace/:object-name
        url = '/sessions/' + session_id + '/workspace/model'
        adapters.append((host + url, adapter(url, 'POST', status_code=200)))

        # 3. - Take snapshot: POST /sessions/:id/snapshot
        url = '/sessions/' + session_id + '/snapshot'
        res = {'snapshotId': snapshot_id}
        adapters.append((host + url, adapter(url, 'POST', json=res)))

        # 4. - Close session: DELETE /sessions/:id
        url = '/sessions/' + session_id        
        adapters.append((host + url, adapter(url, 'DELETE', status_code=200)))
        
        # 5. - Publish service: POST /services/:name/:version
        url = '/services/' + name + '/' + version        
        adapters.append((host + url, adapter(url, 'POST', status_code=201)))

        # 6. - Delete snapshot: DELETE 
        url = '/snapshots/' + snapshot_id        
        adapters.append((host + url, adapter(url, 'DELETE', status_code=200)))

        # Final. - Get service: GET 
        url = '/services/' + name + '/' + version
        res = service_meta
        adapters.append((host + url, adapter(url, requests_mock.ANY, json=res)))
                
        mls = client(adapters)        
        service = mls.deploy_service(name, **kwargs)
        cap = service.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    @pytest.mark.parametrize('version', ['v1', None])
    def test_get_service_with_adapters(self, client_adapters, service_meta,
                                       version):

        response = [service_meta] if version is None else service_meta

        client = client_adapters
        url = services_resource(service_meta['name'], version)
        adapter = requests_mock.Adapter()
        adapter.register_uri('GET', url, json=response)
        service = client(adapter).get_service(service_meta['name'],
                                              version=version)

        cap = service.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    @pytest.mark.parametrize(
        'name, version, response', [
            ('foo-service', 'v1', [
                {'name': 'foo-service', 'version': 'v1'},
             ]),
            ('baz-service', None, [
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'}
             ]),
             (None, None, [
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'},
                {'name': 'foo-service', 'version': 'v2'},
                {'name': 'foo-service', 'version': 'v1'}
             ])
        ])
    def test_list_services_with_adapters(self, client_adapters, name, version,
                                         response):
        client = client_adapters
        url = services_resource(name, version)
        adapter = requests_mock.Adapter()
        adapter.register_uri('GET', url, json=response)
        mls = client(adapter)

        services = mls.list_services(name, version=version)
        assert services == response

    @pytest.mark.parametrize(
        'name, version, status_code', [
            ('foo-service', 'v1', 200),
            ('bar-service', 'v1.0', 200),
            ('baz-service', 'v1.2.2', 200)
        ])    
    def test_delete_service_with_adapters(self, client_adapters, name, version, status_code):
        client = client_adapters
        url = services_resource(name, version)
        adapter = requests_mock.Adapter()
        adapter.register_uri('DELETE', url, status_code=status_code)

        mls = client(adapter)
        assert mls.delete_service(name, version=version)

