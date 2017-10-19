# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest
import os
import pickle
from azureml.deploy import DeployClient, Operationalization
from azureml.deploy.server import MLServer

WS_PATCH_TARGET = 'azureml.deploy.server.services.WebServiceService'
HOST = 'http://localhost:12800'
model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..","..","..","assets")


class TestDeployClient:

    @pytest.fixture
    def service_meta(self):
        return {
            'name': 'transmission',
            'version': 'v1',
            'description': 'Support the transmission...',
            'createTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'outputFileNames': ['file1.png', 'file2.png'],
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
            ],
            'operationId': 'transmission'
        }

    @pytest.fixture
    def realtime_meta(self):
        return {
            'name': 'transmission',
            'version': 'v1',
            'description': 'Realtime Service...',
            'createTime': 'YYYY-MM-DD',
            'snapshotId': 'snapshot-3456789312345',
            'inputParameterDefinitions': [
                {
                    'name': 'inputData',  # convention for realtime
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

    @pytest.mark.parametrize(
        'use', [
            'azureml.deploy.server.MLServer',
            'MLServer',
            MLServer,  # by module ref
            ('azureml.deploy.server.MLServer', os.path.join(os.getcwd(), os.path.normpath('azureml/deploy/server/mlserver.py')))
        ])
    def test_module_load(self, use):        
        ml = DeployClient(HOST, use=use)
        assert isinstance(ml, Operationalization)

    @pytest.mark.parametrize(
        'use', [
            'azureml.deploy.server.DoesNotExist',
            'DoesNotExist',
            True,
            12345,
            TypeError,  # Test Module ref not implementing `Operationalization`
            ('DoesNotExist', '/does_not_exist.py')
        ])
    def test_module_load_failure(self, use):
        with pytest.raises(ImportError) as e_info:
            ml = DeployClient(HOST, use=use)

    def test_fluent_deploy(self, mocker, service_meta):
        mocker.patch(WS_PATCH_TARGET + '.create_service')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = service_meta

        def init():
            print('init')

        def add_one(x):
            return x + 1

        model = 'the_model'
        local_obj = 100            
        
        ml = DeployClient(HOST, use='MLServer')

        api = ml.service(service_meta['name'])\
            .version(service_meta['version'])\
            .code_fn(add_one, init)\
            .inputs(hp=float, wt=float)\
            .outputs(answer=float)\
            .models(model=model)\
            .objects(local_obj=local_obj)\
            .artifacts(service_meta['outputFileNames'])\
            .description(service_meta['description'])\
            .deploy()

        cap = api.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    def test_fluent_deploy_realtime(self, mocker, realtime_meta):
        mocker.patch(WS_PATCH_TARGET + '.create_realtime')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = realtime_meta

        model = 'the_model'
        s_model = pickle.dumps(model)

        ml = DeployClient(HOST, use='MLServer')

        api = ml.realtime_service(realtime_meta['name']) \
            .version(realtime_meta['version']) \
            .serialized_model(s_model) \
            .description(realtime_meta['description']) \
            .deploy()

        cap = api.capabilities()

        assert cap['name'] == realtime_meta['name']
        assert cap['version'] == realtime_meta['version']
        assert cap['description'] == realtime_meta['description']

    def test_fluent_redeploy(self, mocker, service_meta):
        mocker.patch(WS_PATCH_TARGET + '.update_service')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = service_meta

        def init():
            print('init')

        def add_one(x):
            return x + 1

        model = 'the_model'
        local_obj = 100
                
        ml = DeployClient(HOST, use='MLServer')

        api = ml.service(service_meta['name'])\
            .version(service_meta['version'])\
            .code_fn(add_one, init)\
            .inputs(hp=float, wt=float)\
            .outputs(answer=float)\
            .models(model=model)\
            .objects(local_obj=local_obj)\
            .artifacts(service_meta['outputFileNames'])\
            .description(service_meta['description'])\
            .redeploy()

        cap = api.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    def test_fluent_redeploy_realtime(self, mocker, realtime_meta):
        mocker.patch(WS_PATCH_TARGET + '.update_realtime_service')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = realtime_meta

        model = 'the_model'
        s_model = pickle.dumps(model)

        ml = DeployClient(HOST, use='MLServer')

        api = ml.realtime_service(realtime_meta['name']) \
            .version(realtime_meta['version']) \
            .serialized_model(s_model) \
            .description(realtime_meta['description']) \
            .redeploy()

        cap = api.capabilities()

        assert cap['name'] == realtime_meta['name']
        assert cap['version'] == realtime_meta['version']
        assert cap['description'] == realtime_meta['description']

    def test_fluent_multi_line_deploy(self, mocker, service_meta):
        mocker.patch(WS_PATCH_TARGET + '.create_service')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = service_meta

        def init():
            print('init')

        def add_one(x):
            return x + 1

        model = 'the_model'
        local_obj = 100

        ml = DeployClient(HOST, use='azureml.deploy.server.MLServer')

        service_def = ml.service(service_meta['name'])
        service_def.version(service_meta['version'])
        service_def.code_fn(add_one, init)
        service_def.inputs(ht=float, wt=float)
        service_def.outputs(answer=float)
        service_def.models(model=model)
        service_def.objects(local_obj=local_obj)
        service_def.artifacts(service_meta['outputFileNames'])
        service_def.description(service_meta['description'])

        api = service_def.deploy()
        cap = api.capabilities()

        assert cap['name'] == service_meta['name']
        assert cap['version'] == service_meta['version']
        assert cap['description'] == service_meta['description']

    def test_fluent_multi_line_deploy_realtime(self, mocker, realtime_meta):
        mocker.patch(WS_PATCH_TARGET + '.create_realtime')
        mock = mocker.patch(WS_PATCH_TARGET + '.get_service')
        mock.return_value = realtime_meta

        model = 'the_model'
        s_model = pickle.dumps(model)

        ml = DeployClient(HOST, use='MLServer')

        service_def = ml.realtime_service(realtime_meta['name'])
        service_def.version(realtime_meta['version'])
        service_def.serialized_model(s_model)
        service_def.alias(realtime_meta['operationId'])
        service_def.description(realtime_meta['description'])

        api = service_def.deploy()
        cap = api.capabilities()

        assert cap['name'] == realtime_meta['name']
        assert cap['version'] == realtime_meta['version']
        assert cap['description'] == realtime_meta['description']
