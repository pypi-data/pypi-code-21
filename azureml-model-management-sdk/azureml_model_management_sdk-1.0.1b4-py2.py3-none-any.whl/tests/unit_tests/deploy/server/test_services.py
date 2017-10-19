# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest
import requests_mock
import os
from azureml.common import HttpClient, Configuration
from azureml.deploy.server import WebServiceService
import pickle

WS_PATCH_TARGET = 'azureml.deploy.server.services.WebServiceService'
model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","..","..","assets")


def services_resource(name=None, version=None):
    resource = '/services'

    if name is not None:
        resource += '/' + name

    if version is not None:
        resource += '/' + version

    return Configuration().host + resource


class TestWebServiceService:
    
    @pytest.fixture
    def service_factory(self):
        def create_webservice(resource, method, json=None, status_code=None):            
            host = Configuration().host
            http_client = HttpClient(host = host)

            # mount mock adapter
            url = resource
            adapter = requests_mock.Adapter()
            if json is not None:
                adapter.register_uri(method, url, json=json)
            else:
                adapter.register_uri(method, url, status_code=status_code)
            http_client.mount(url, adapter)

            return WebServiceService(http_client)

        return create_webservice

    @pytest.fixture
    def adapter(self):
        def factory(resource, method, json=None, status_code=None): 
            url = Configuration().host + resource
            adapter = requests_mock.Adapter()
            if json is not None:
                adapter.register_uri(method, url, json=json)
            else:
                adapter.register_uri(method, url, status_code=status_code)

            return adapter

        return factory

    def test_update_service(self, adapter):
        name = 'add-one'
        version = 'v1.1.0'
        host = Configuration().host
        adapters = []
        
        Configuration().debug = True        

        session_id = 'session-id-123456'
        snapshot_id = 'snapshot-id-123456'

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
            'inputs': {'x': float},
            'outputs': {'answer': float},
            'artifacts': ['histogram.png'],
            'description': 'The Description of the `add-one` service'
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

        # 3. - Take snanpshot: POST /sessions/:id/snapshot
        url = '/sessions/' + session_id + '/snapshot'
        res = {'snapshotId': snapshot_id}
        adapters.append((host + url, adapter(url, 'POST', json=res)))

        # 4. - Close session: DELETE /sessions/:id
        url = '/sessions/' + session_id        
        adapters.append((host + url, adapter(url, 'DELETE', status_code=200)))
        
        # 5. - Publish service: PATCH /services/:name/:version
        url = '/services/' + name + '/' + version        
        #adapters.append((host + url, adapter(url, 'PATCH', status_code=201)))
        adapters.append((host + url, adapter(url, 'PATCH', json=version)))

        # 6. - Delete snapshot: DELETE 
        url = '/snapshots/' + snapshot_id        
        adapters.append((host + url, adapter(url, 'DELETE', status_code=200)))
       
        # --- mount mock adapter ---        
        http_client = HttpClient(host=Configuration().host)

        for adapter_set in adapters:
            prefix = adapter_set[0]
            adapter = adapter_set[1]
            http_client.mount(prefix, adapter)

        service = WebServiceService(http_client)

        #assert service.update_service(name, **kwargs).status_code == 201
        assert service.update_service(name, **kwargs) == version


    def test_update_realtime(self, adapter, mocker):
        name = 'py_realtime'
        version = '1.1.0'
        host = Configuration().host
        adapters = []

        Configuration().debug = True

        mock = mocker.patch(WS_PATCH_TARGET + '.' + '_check_serialized_model')
        mock.return_value = True

        # --- Or Publish service via `kwargs` dictionary ---
        # -- serialize fake model
        model = 'the_model'
        s_model = pickle.dumps(model)

        kwargs = {
            'version': version,
            'serialized_model': s_model,
            'description': 'The Description of the `add-one` service'
        }

        # 1. - Publish Realtime Service
        url = '/realtime-services/{}/{}'.format(name,version)
        res = {"status_code": 201, "name": name, "version":version}
        adapters.append((host + url, adapter(url, 'PATCH', json=res)))

        # --- mount mock adapter ---
        http_client = HttpClient(host=Configuration().host)

        for adapter_set in adapters:
            prefix = adapter_set[0]
            adapter = adapter_set[1]
            http_client.mount(prefix, adapter)

        service = WebServiceService(http_client)
        res = service.update_realtime_service(name, **kwargs)
        assert res['status_code'] == 201

    @pytest.mark.parametrize(
        'model, error_message, version', [
            (b'testByteString',
             "must be serialized by 'rx_serialize_model' function",
             '1.0.0'),
            ('testModel',
             "must be serialized by 'rx_serialize_model' function",
             '1.0.0'),
            ('',
             "The serialized_model parameter can't be None",
             '1.0.0'),
            (None,
             "The serialized_model parameter can't be None",
             '1.0.0'),
            (b'blobtestByteString',
             "Missing the required parameter `version`",
             None)
        ])
    def test_update_realtime_failure(self, adapter, mocker, model, error_message, version):
        name = 'py_realtime'
        host = Configuration().host
        adapters = []

        Configuration().debug = True

        # --- Or Publish service via `kwargs` dictionary ---

        kwargs = {
            'version': version,
            'serialized_model': model,
            'description': 'The Description of the `add-one` service'
        }
        http_client = HttpClient(host=Configuration().host)

        with pytest.raises(ValueError) as e_info:
            service = WebServiceService(http_client)
            service.update_realtime_service(name, **kwargs)

        assert error_message in str(e_info.value)

    def test_create_service(self, adapter):
        name = 'add-one'
        version = 'v1.1.0'
        host = Configuration().host
        adapters = []
        
        Configuration().debug = True        

        session_id = 'session-id-123456'
        snapshot_id = 'snapshot-id-123456'

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
            'inputs': {'x': float},
            'outputs': {'answer': float},
            'artifacts': ['histogram.png'],
            'description': 'The Description of the `add-one` service'
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
        res = { 'snapshotId': snapshot_id }        
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
       
        # --- mount mock adapter ---        
        http_client = HttpClient(host = Configuration().host)

        for adapter_set in adapters:
            prefix = adapter_set[0]
            adapter = adapter_set[1]
            http_client.mount(prefix, adapter)

        service = WebServiceService(http_client)

        assert service.create_service(name, **kwargs).status_code == 201


    def test_create_realtime(self, adapter, mocker):
        name = 'python_realtime'
        version = 'v1.1.0'
        host = Configuration().host
        adapters = []

        Configuration().debug = True

        mock = mocker.patch(WS_PATCH_TARGET + '.' + '_check_serialized_model')
        mock.return_value = True

        # --- Or Publish service via `kwargs` dictionary ---
        # create fake model and serialize it
        model = 'the_model'
        s_model = pickle.dumps(model)

        kwargs = {
            'version': version,
            'serialized_model': s_model,
            'description': 'The Description of the `add-one` service'
        }

        # 1. - Publish Realtime Service
        url = '/realtime-services/{}/{}'.format(name,version)
        res = {"status_code": 201, "name":name, "version":version}
        adapters.append((host + url, adapter(url, 'POST', json=res)))

        # --- mount mock adapter ---
        http_client = HttpClient(host=Configuration().host)

        for adapter_set in adapters:
            prefix = adapter_set[0]
            adapter = adapter_set[1]
            http_client.mount(prefix, adapter)

        service = WebServiceService(http_client)
        res = service.create_realtime(name, **kwargs)
        assert res['status_code'] == 201

    @pytest.mark.parametrize(
        'model, error_message, version', [
            (b'testByteString',
             "must be serialized by 'rx_serialize_model' function",
             '1.0.0'),
            ('testModel',
             "must be serialized by 'rx_serialize_model' function",
             '1.0.0'),
            ('',
             "The serialized_model parameter can't be None",
             '1.0.0'),
            (None,
             "The serialized_model parameter can't be None",
             '1.0.0')
        ])
    def test_create_realtime_failure(self, adapter, mocker, model, error_message, version):
        name = 'py_realtime'
        host = Configuration().host

        Configuration().debug = True

        # --- Or Publish service via `kwargs` dictionary ---

        kwargs = {
            'version': version,
            'serialized_model': model,
            'description': 'The Description of the `add-one` service'
        }
        http_client = HttpClient(host=Configuration().host)

        with pytest.raises(ValueError) as e_info:
            service = WebServiceService(http_client)
            service.create_realtime(name, **kwargs)

        assert error_message in str(e_info.value)


    @pytest.mark.parametrize(
        'name, version, status_code', [
            ('foo-service', 'v1', 200),
            ('bar-service', 'v1.0', 200),
            ('baz-service', 'v1.2.2', 200)
        ])    
    def test_delete_service(self, service_factory, name, version, status_code):
        url = services_resource(name, version)
        service = service_factory(url, 'DELETE', status_code=status_code)        
        assert service.delete_service(name, version).status_code == status_code        
   
    @pytest.mark.parametrize(
        'response', [
             ([]),
             ([
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'},
                {'name': 'foo-service', 'version': 'v2'},
                {'name': 'foo-service', 'version': 'v1'}
             ])
        ])
    def test_get_all_services(self, service_factory, response):
        url = services_resource()        
        service = service_factory(url, 'GET', json=response)        
        assert service.get_all_services() == response        
    
    @pytest.mark.parametrize(
        'name, response', [
            ('foo-service', [{'name': 'foo-service', 'version': 'v1'}]),
            ('baz-service', [
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'}
            ])
        ])   
    def test_get_service_versions(self, service_factory, name, response):
        url = services_resource(name)        
        service = service_factory(url, 'GET', json=response)        
        assert service.get_service_versions(name) == response
    
    @pytest.mark.parametrize(
        'name, version, response', [
            ('foo-service', 'v1', {'name': 'foo-service', 'version': 'v1'})
        ])
    def test_get_service(self, service_factory, name, version, response):
        url = services_resource(name, version)        
        service = service_factory(url, 'GET', json=response)        
        assert service.get_service(name, version) == response

    @pytest.mark.parametrize(
        'name, response', [
            ('foo-service', [{'name': 'foo-service', 'version': 'v1'}]),
            ('baz-service', [
                {'name': 'baz-service', 'version': 'v3'},
                {'name': 'baz-service', 'version': 'v2'},
                {'name': 'baz-service', 'version': 'v1'}
            ])
        ]) 
    def test_get_latest_service(self, service_factory, name, response):
        url = services_resource(name)        
        service = service_factory(url, 'GET', json=response)
        assert service.get_latest_service(name) == response[-1]
