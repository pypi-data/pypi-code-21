# ------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for 
# license information.
# ------------------------------------------------------------------------------

# -*- coding: utf-8; tab-width: 4; indent-tabs-mode: t; python-indent: 4 -*-

"""
    MLServer
"""

from __future__ import absolute_import

# python 2 and python 3 compatibility library
from six import iteritems
import json


class ServicesApi(object):
    """
    ServicesApi
    """

    def __init__(self, http_client):
        self._http_client = http_client


    def delete_web_service_version(self, name, version, **kwargs):
        """
        Delete Service
        Deletes the published web service for the logged in user.
        This method makes a synchronous HTTP request by default. 
            
        :param str name: The name of the published web service. (required)
        :param str version: The version of the published web service. (required)
        :return: None                 
        """
        
        return self._http_client.delete('/services/' + name + '/' + version)
        
    def get_all_web_service_versions_by_name(self, name, **kwargs):
        """
        Get Service by `name`
        Lists all the published services with the provided `name`.
        This method makes a synchronous HTTP request by default. 

        :param str name: name of the published web service. (required)
        :return: list[InlineResponse2001]
                 If the method is called asynchronously,
                 returns the request thread.
        """

        resource = '/services/' + name
        return self._http_client.get(resource).json()

    def get_all_web_services(self, **kwargs):
        """
        Get Services
        Lists all the published services.
        This method makes a synchronous HTTP request by default. 

        :param callback function: The callback function
            for asynchronous request. (optional)
        :return: list[InlineResponse2001]
        """
        #self._http_client.set_header("Authorization", self._http_client.Authorization)
        return self._http_client.get('/services').json()

    def get_web_service_version(self, name, version, **kwargs):
        """
        Get Service by `name` and `version`
        Lists all the published services with the provided `name` and `version`.
        This method makes a synchronous HTTP request by default. 

        :param str name: The name of the published web service. (required)
        :param str version: The version of the published web service. (required)
        :return: list[InlineResponse2001]                 
        """

        resource = '/services/' + name + '/' + version
        return self._http_client.get(resource).json()
   
    def patch_web_service_version(self, name, version, patch_request, **kwargs):
        """
        Patch Service
        Updates the published service.
        This method makes a synchronous HTTP request by default. 
        :param str name: The name of the published web service. (required)
        :param str version: The version of the published web service. (required)
        :param PatchRequest patch_request: Publish Web Service request details. (required)
        :return: str
        """

        all_params = ['name', 'version', 'patch_request']
        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method patch_web_service_version" % key
                )
            params[key] = val

        del params['kwargs']
        
        # verify the required parameter 'name' is set
        if ('name' not in params) or (params['name'] is None):
            raise ValueError("Missing the required parameter `name` when calling `patch_web_service_version`")
        # verify the required parameter 'version' is set
        if ('version' not in params) or (params['version'] is None):
            raise ValueError("Missing the required parameter `version` when calling `patch_web_service_version`")
        # verify the required parameter 'patch_request' is set
        if ('patch_request' not in params) or (params['patch_request'] is None):
            raise ValueError("Missing the required parameter `patch_request` when calling `patch_web_service_version`")

        body = patch_request.to_dict()
            
        resource = '/services/' + name + '/' + version
        body = json.dumps(patch_request.to_dict())
        return self._http_client.patch(resource, data=body).json()

    def publish_web_service(self, name, publish_request, **kwargs):
        """
        Create Service by `name`
        Publish the web services for the logged in user with given name and a 
        unique version.
        
        :param str name: name of the published web service. (required)
        :param PublishRequest publish_request: Publish Web Service request 
        details. (required)
        :return: str                
        """

        all_params = ['name', 'publish_request']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method publish_web_service" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'name' is set
        if ('name' not in params) or (params['name'] is None):
            raise ValueError("Missing the required parameter `name` when calling `publish_web_service`")
        # verify the required parameter 'publish_request' is set
        if ('publish_request' not in params) or (params['publish_request'] is None):
            raise ValueError("Missing the required parameter `publish_request` when calling `publish_web_service`")
        
        body = publish_request.to_dict()

        return self._http_client.post('/services/' + name, json=body).json()

    def publish_web_service_version(self, name, version, publish_request, **kwargs):
        """
        Create Service by `name` and `version`
        Publish the web service for the logged in user with given name and 
        version.        

        :param str name: name of the published web service. (required)
        :param str version: version of the published web service. (required)
        :param PublishRequest1 publish_request: Publish Service request details. 
        (required)
        :return: str
        """

        all_params = ['name', 'version', 'publish_request']

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method publish_web_service_version" % key
                )
            params[key] = val
        
        del params['kwargs']

        # verify the required parameter 'name' is set
        if ('name' not in params) or (params['name'] is None):
            raise ValueError("Missing the required parameter `name` when calling `publish_web_service_version`")
        # verify the required parameter 'version' is set
        if ('version' not in params) or (params['version'] is None):
            raise ValueError("Missing the required parameter `version` when calling `publish_web_service_version`")
        # verify the required parameter 'publish_request' is set
        if ('publish_request' not in params) or (params['publish_request'] is None):
            raise ValueError("Missing the required parameter `publish_request` when calling `publish_web_service_version`")
                
        body = publish_request.to_dict()
        resource = '/services/' + name + '/' + version

        return self._http_client.post(resource, json=body)

    def publish_realtime_service(self, name, **kwargs):
        """
        Create Realtime Service by `name`
        Publish the Realtime services for the logged in user with given name and a
        unique generated version.

        :param str name: name of the published web service. (required)
        :return: str
        """
        # verify the required parameter 'name' is set
        if ( name is None):
            raise ValueError("Missing the required parameter `name` when calling `publish_realtime_service`")
        model = kwargs.get("serialized_model")
        version = kwargs.get('version')
        resource = '/realtime-services/{}/{}'.format(name,version) if version \
                    else '/realtime-services/{}'.format(name)
        body = {
            'description' : kwargs.get("description"),
            'operationId' : kwargs.get("alias"),
            }
        header = {'Accept':"application/json",
                  "Content-Type":None}
        files = {'model': model}
        response = self._http_client.post(resource, data = body, headers = header, files = files)
        return response.json()

    def patch_realtime_service(self, name, **kwargs):
        """
        Patch Service
        Updates the published realtime service.
        This method makes a synchronous HTTP request by default.
        
        :param str name: The name of the published web service. (required)
        :return: str
        """
        # verify the required parameter 'name' is set
        if ( name is None):
            raise ValueError("Missing the required parameter `name` when calling `patch_realtime_service`")
        version = kwargs.get('version')
        resource = '/realtime-services/' + name + '/' + version
        model = kwargs.get("serialized_model")
        body = {
            'description' : kwargs.get("description"),
            'operationId' : kwargs.get("alias"),
            }
        header = {'Accept':"application/json",
                  "Content-Type":None}
        files = {'model': model}
        response = self._http_client.patch(resource, data = body, headers = header, files = files)
        return response.json()