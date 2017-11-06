# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

import pytest

from azureml.deploy import ServiceDefinition, Operationalization


class MockOperationalization(Operationalization):

    def __init__(self):
        pass

    def initializer(self, api_client, config):
        pass

    def destructor(self):
        pass

    def authentication(self, context):
        pass

    def get_service(self, name):
        pass

    def list_services(self, name=None, **kwargs):
        pass

    def delete_service(self, name):
        pass

    def deploy_service(self, name, **kwargs):
        return kwargs

    def redeploy_service(self, name, force=False, **kwargs):
        return kwargs

    def deploy_realtime(self, name, **kwargs):
        pass

    def redeploy_realtime(self, name, force=False, **kwargs):
        pass

    def service(self, name):
        return ServiceDefinition(name, self)


    def realtime_service(self, name):
        pass


class TestOperationalization:

    @pytest.fixture
    def sd(self):
        return MockOperationalization().service('service')

    def test_service_definition_objects_insert(self, sd):
        objects = {'i': 5, 's': 'String', 'b': True, 'f': 1.2345}
        sd.objects(**objects)

        assert sd.deploy()['objects'] == objects

    def test_service_definition_model_insert(self, sd):
        models = {'i': 5, 's': 'String', 'b': True, 'f': 1.2345}
        sd.models(**models)

        assert sd.deploy()['models'] == models



