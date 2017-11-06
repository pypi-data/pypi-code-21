# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
services

Overview
========
The service layer defines a simple boundary and its set of available operations 
from the perspective of interfacing client layers. It encapsulates the 
application's business logic.
"""

from six import iteritems
from azureml.common.utils import to_self_execution_block, function_args
from .encoding_type import EncodingType
from .apis import ServicesApi, SessionsApi, SnapshotsApi
from .models import (
    CreateSessionRequest, 
    CreateSnapshotRequest, 
    ExecuteRequest,
    ServicesInputParameterDefinitions,
    ServicesOutputParameterDefinitions,
    PublishRequest,
    PatchRequest
)

import dill
import logging


log = logging.getLogger(__name__)

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


class WebServiceService(object):

    def __init__(self, http_client):
        self._http_client = http_client
        self._api = ServicesApi(self._http_client)        

    def create_service(self, name, **kwargs):        
        response = env = None
                
        try:            
            env = AuthoringEnvironment(
                SessionService(self._http_client),
                SnapshotService(self._http_client))

            pub_request = env.create(PublishRequest(), **kwargs)
                                   
            # Publish Service
            version = kwargs.get('version')

            log.debug('`publish_request`: \n   %s', pub_request)  

            if version is not None:
                response = self._api.publish_web_service_version(
                    name, version, pub_request)
            else:
                response = self._api.publish_web_service(name, pub_request)
            
        finally:
            if env is not None:
                env.destroy()

        return response

    def create_realtime(self, name, **kwargs):
        model = kwargs.get('serialized_model')
        if model == None or len(model) == 0:
            raise ValueError("The serialized_model parameter can't be None for "
                             "deployment of realtime_service")
        if not self._check_serialized_model(model):
            raise ValueError("Realtime serialized_model must be serialized by "
                             "'rx_serialize_model' function in RevoScalePy "
                             "Package")
        response = self._api.publish_realtime_service(name, **kwargs)
        return response

    def update_service(self, name, **kwargs):        
        response = env = None      
                
        try:            
            env = AuthoringEnvironment(
                SessionService(self._http_client),
                SnapshotService(self._http_client))

            patch_request = env.create(PatchRequest(), **kwargs)
                                               
            version = kwargs.get('version')

            # -- If no version supplied update the latest --
            if version is None:
                try:
                    version = self.get_latest_service(name).version
                except Exception:
                    msg = 'Attempt to patch latest service version failed for'\
                        '{0}'.format(name)
                    raise ValueError(msg)

            # Do not update the IO if IO is None/empty
            # We need to differentiate between update of `void` IO versus keep 
            # IO the same. Setting them to `None` will omit from patch payload 
            # and ignored
            if kwargs.get('inputs') is None:
                patch_request.input_parameter_definitions = None

            if kwargs.get('outputs') is None:
                patch_request.output_parameter_definitions = None

            if kwargs.get('artifacts') is None:
                patch_request.output_file_names = None

            log.debug('`patch_request`: \n   %s', patch_request)

            response = self._api.patch_web_service_version(
                name, version, patch_request)
            
        finally:
            if env is not None:
                env.destroy()

        return response

    def update_realtime_service(self, name, **kwargs):
        model = kwargs.get('serialized_model')
        version = kwargs.get('version')
        if model == None or len(model) == 0:
            raise ValueError("The serialized_model parameter can't be None for "
                             "redeployment of realtime_service")
        if not self._check_serialized_model(model):
            raise ValueError("Realtime serialized_model must be serialized by "
                             "'rx_serialize_model' function in RevoScalePy "
                             "Package")
        if (version is None):
            raise ValueError("Missing the required parameter `version` when "
                             "calling `update_realtime_service`")
        return self._api.patch_realtime_service(name, **kwargs)

    def delete_service(self, name, version):
        return self._api.delete_web_service_version(name, version)

    def get_all_services(self):        
        services = self._api.get_all_web_services()
        return services
    
    def get_service_versions(self, name):
        services = self._api.get_all_web_service_versions_by_name(name)
        return services
    
    def get_service(self, name, version):
        service = self._api.get_web_service_version(name, version)
        if len(service) == 0 or not service:
            return []
        return service[0] if isinstance(service, list) else service

    def get_latest_service(self, name):
        service = self._api.get_all_web_service_versions_by_name(name)
        if len(service) == 0 or not service:
            return []
        return service[-1]

    def _check_serialized_model(self, model):
        """
        Check if the model is serialized by rx_serialize_model function

        :param model: the model byte string
        :return: true if model is properly serialized
        """
        if not isinstance(model, bytes) or model[:4] != b"blob":
            return False
        return True

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


class SessionService(object):

    def __init__(self, http_client):
        self._api = SessionsApi(http_client)
        
    def create_session(self):
        response = self._api.create_session(CreateSessionRequest(
            runtime_type='Python'))
        return response
    
    def close_session(self, session_id):
        self._api.close_session(session_id)

    def execute_code(self, session_id, code):
        execute_request = ExecuteRequest()
        execute_request.code = code
        self._api.execute_code(session_id, execute_request)

    def upload_file(self, session_id, file_handle):
        self._api.upload_file(session_id, file_handle)

    def set_workspace_object(self, session_id, object_name, object_value):
        try:
            serialized = dill.dumps(object_value)
        except Exception as e:
            msg = 'Error serializing {0}\n{1}\n{2}\n{3}'.format(
                object_name,
                object_value,
                type(e).__name__,
                str(e))

            raise ValueError(msg)

        self._api.set_workspace_object(session_id, object_name, serialized)

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


class SnapshotService(object):

    def __init__(self, http_client):
        self._api = SnapshotsApi(http_client)
    
    def create_snapshot(self, session_id):        
        return self._api.create_snapshot(session_id, CreateSnapshotRequest())

    def delete_snapshot(self, snapshot_id):
        return self._api.delete_snapshot(snapshot_id)

# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #
# ------------------------------------------------------------------------ #


class AuthoringEnvironment(object):

    def __init__(self, session_service, snapshot_service):        
        self._session = None
        self._snapshot = None
        self._session_service = session_service
        self._snapshot_service = snapshot_service
    
    def create(self, request, **kwargs):
        """
        Helper to create a publish/update request environment workflow.
        """

        # -- assert `empty` defaults --
        if kwargs.get('objects') is None:
            kwargs['objects'] = {}

        if kwargs.get('models') is None:
            kwargs['models'] = {}

        if kwargs.get('artifacts') is None:
            kwargs['artifacts'] = []

        if kwargs.get('inputs') is None:
            kwargs['inputs'] = {}

        if kwargs.get('outputs') is None:
            kwargs['outputs'] = {}

        # validate I/O against supported Encoding-Types
        for k, v in kwargs.get('inputs', {}).items():
            if not EncodingType.from_python(v):
                msg = 'Invalid `encoding` type "{0}" for "{1}"'.format(v, k)
                raise ValueError(msg)
        
        for k, v in kwargs.get('outputs', {}).items():
            if not EncodingType.from_python(v):
                msg = 'Invalid `encoding` type "{0}" for "{1}"'.format(v, k)
                raise ValueError(msg)

        # Create session: POST /sessions
        log.debug('Creating a new `session`.')
        self._session = self._session_service.create_session()
        session_id = self._session.session_id
        log.debug('New `session` created "%s".', session_id)
            
        # Upload session file: POST /sessions/:id/files
        for name, value in iteritems(kwargs.get('models', {})):
            log.debug('Adding `model` "%s" to the workspace.', name)
            self._session_service.set_workspace_object(session_id, name, value)

        for name, value in iteritems(kwargs.get('objects', {})):
            log.debug('Adding `object` "%s" to the workspace.', name)
            self._session_service.set_workspace_object(session_id, name, value)

        # Take snapshot: POST /sessions/:id/snapshot
        log.debug('Taking `snapshot` on session "%s".', session_id)
        self._snapshot = self._snapshot_service.create_snapshot(session_id)
                    
        alias = kwargs.get('alias')
        init = kwargs.get('init_str')
        code = kwargs.get('code_str')

        # input order
        input_order = list(kwargs.get('inputs'))
                        
        # If code-block as a `str` was not found check for function handle
        if code is None and 'code_fn' in kwargs:
            init = kwargs.get('init_fn')
            code = kwargs.get('code_fn')

            if init is not None:
                init = to_self_execution_block(init)

            if code is not None:
                alias = alias if alias else code.__name__
                output = None

                # arg order maters for `code_fn`
                if 'inputs' in kwargs:
                    input_order = function_args(code)

                if 'outputs' in kwargs:
                    output = list(kwargs['outputs'])

                    # can only have one return value for fn, grab the first
                    if len(output) > 0:
                        output = output[0]
                 
                code = to_self_execution_block(code, output=output)
                
        log.debug('`init`: \n   %s', init)
        log.debug('`code`: \n   %s', code)

        inputs = []
        outputs = []

        # -- Inputs --
        input_defs = kwargs.get('inputs')
        for name in input_order:  # fn argument Order is important
            in_type = input_defs.get(name)

            if in_type is None:
                raise ValueError('Input {0} not a code argument.'.format(name))

            inputs.append(ServicesInputParameterDefinitions(
                name=name, type=EncodingType.from_python(in_type)))

        # -- Outputs --
        for name, out_type in iteritems(kwargs.get('outputs', {})):
            outputs.append(ServicesOutputParameterDefinitions(
                name=name, type=EncodingType.from_python(out_type)))
                    
        request.snapshot_id = self._snapshot.snapshot_id
        request.code = code
        request.description = kwargs.get('description')
        request.operation_id = alias
        request.input_parameter_definitions = inputs
        request.output_parameter_definitions = outputs
        request.runtime_type = 'Python'
        request.init_code = init
        request.output_file_names = kwargs.get('artifacts')

        return request    

    def destroy(self):
        session = self._session
        snapshot = self._snapshot
        
        # Close session: DELETE /sessions/:id
        if session is not None:
            log.debug('Closing `session` "%s".', session.session_id)
            self._session_service.close_session(session.session_id)
        
        # Remove snapshot: DELETE /snapshots/:id
        if snapshot is not None:
            log.debug('Deleting `snapshot` "%s".', snapshot.snapshot_id)
            self._snapshot_service.delete_snapshot(snapshot.snapshot_id)
