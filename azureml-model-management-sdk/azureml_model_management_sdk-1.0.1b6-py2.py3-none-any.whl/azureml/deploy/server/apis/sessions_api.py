# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
    MLSServer
"""

from __future__ import absolute_import

# python 2 and python 3 compatibility library
from six import iteritems
from ..models import CreateSessionResponse, ExecuteResponse


class SessionsApi(object):
    """
    
    """

    def __init__(self, http_client):
        self._http_client = http_client

    def close_session(self, id, **kwargs):
        """
        Delete Session
        Close a session and releases all it's associated resources.
        This method makes a synchronous HTTP request by default.
        :param str id: Id of the session to delete. (required)
        :return: str
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id']
      
        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method close_session" % key
                )
            params[key] = val
        
        del params['kwargs']

        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `close_session`")
        
        return self._http_client.delete('/sessions/' + id)

    def create_session(self, create_session_request, **kwargs):
        """
        Create Session
        Create a new session.
        This method makes a synchronous HTTP request by default. 

        :param CreateSessionRequest create_session_request: Properties of the
        new session. (required)
        :return: InlineResponse201
                 If the method is called asynchronously,
                 returns the request thread.
        """

        create_session_request.runtime = 'Python'
        body = create_session_request.to_dict()        
        response = self._http_client.post('/sessions', json=body).json()
        return CreateSessionResponse(session_id=response.get('sessionId'))

    def execute_code(self, id, execute_request, **kwargs):
        """
        Execute Code
        Executes code in the context of a specific session.
        
        :param str id: Id of the session. (required)
        :param ExecuteRequest execute_request: code that needs to be executed 
        (required)
        :return: InlineResponse2003
        """

        all_params = ['id', 'execute_request']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method execute_code" % key
                )
            params[key] = val
        
        del params['kwargs']

        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `execute_code`")
        # verify the required parameter 'execute_request' is set
        if ('execute_request' not in params) or (params['execute_request'] is None):
            raise ValueError("Missing the required parameter `execute_request` when calling `execute_code`")
        
        resource = '/sessions/' + id + '/execute'
        body = execute_request.to_dict()        
        response = self._http_client.post(resource, json=body).json()

        return ExecuteResponse(
            success=response['success'],
            error_message=response['errorMessage'],
            output_parameters=response['outputParameters'],
            console_output=response['consoleOutput'],
            changed_files=response['changedFiles']
        )
   
    def set_workspace_object(self, id, object_name, serialized_object, **kwargs):
        """
        Create Workspace Object
        Upload a serialized object into the session.

        :param str id: Id of the session. (required)
        :param str object_name: Name of the object. (required)
        :param str serialized_object: The binary file that contains a serialized
        object to be uploaded. The binary file `Content-Type` should be
        `application/octet-stream`. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'object_name', 'serialized_object']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method set_workspace_object" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling "
                             "`set_workspace_object`")
        # verify the required parameter 'object_name' is set
        if ('object_name' not in params) or (params['object_name'] is None):
            raise ValueError("Missing the required parameter `object_name` when"
                             " calling `set_workspace_object`")
        # verify the required parameter 'serialized_object' is set
        if ('serialized_object' not in params) or (params['serialized_object'] is None):
            raise ValueError("Missing the required parameter `serialized_"
                             "object`when calling `set_workspace_object`")

        resource = '/sessions/'+ id + '/workspace/' + object_name

        body = None
        if 'serialized_object' in params:
            body = params['serialized_object']

        headers = {'Content-Type': 'application/octet-stream'}

        response = self._http_client.post(resource, data=body, headers=headers)

    def upload_session_file(self, id, file, **kwargs):
        """
        Load File
        Loads a file into the session working directory. The uploaded file name is extracted from the file and if another file with the same name already exists in the working directory, the file will be overwritten.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.upload_session_file_with_http_info(id, file, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param str id: Id of the session. (required)
        :param file file: The file to be uploaded to the workspace. (required)
        :return: None
                 If the method is called asynchronously,
                 returns the request thread.
        """

        create_session_request.runtime = 'Python'
        body = create_session_request.to_dict()        
        response = self._http_client.post('/sessions', json=body).json()
        return CreateSessionResponse(session_id = response.get('sessionId'))

        resource = '/sessions/' + id + '/files'
        headers = {}
        headers['Accept'] = 'text/plain'
        headers['Content-Type'] = 'multipart/form-data'
        
        files = { 'file': file }
        return self._http_client.post(resource, files=files, headers=headers)

        all_params = ['id', 'file']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method upload_session_file" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `upload_session_file`")
        # verify the required parameter 'file' is set
        if ('file' not in params) or (params['file'] is None):
            raise ValueError("Missing the required parameter `file` when calling `upload_session_file`")

        resource = '/sessions/{id}/files'.replace('{format}', 'json')
        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        header_params = {}

        form_params = []
        local_var_files = {}
        if 'file' in params:
            local_var_files['file'] = params['file']

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['text/plain'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['multipart/form-data'])
