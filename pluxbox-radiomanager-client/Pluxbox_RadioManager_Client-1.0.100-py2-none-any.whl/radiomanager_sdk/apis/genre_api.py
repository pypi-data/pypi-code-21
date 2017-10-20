# coding: utf-8

"""
    RadioManager

    RadioManager

    OpenAPI spec version: 2.0
    Contact: support@pluxbox.com
    Generated by: https://github.com/swagger-api/swagger-codegen.git
"""


from __future__ import absolute_import

import sys
import os
import re

# python 2 and python 3 compatibility library
from six import iteritems

from ..configuration import Configuration
from ..api_client import ApiClient


class GenreApi(object):
    """
    NOTE: This class is auto generated by the swagger code generator program.
    Do not edit the class manually.
    Ref: https://github.com/swagger-api/swagger-codegen
    """

    def __init__(self, api_client=None):
        config = Configuration()
        if api_client:
            self.api_client = api_client
        else:
            if not config.api_client:
                config.api_client = ApiClient()
            self.api_client = config.api_client

    def get_genre_by_id(self, id, **kwargs):
        """
        Get genre by id
        Get genre by id
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_genre_by_id(id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param int id: ID of Genre **(Required)** (required)
        :param int external_station_id: Query on a different (content providing) station *(Optional)*
        :return: GenreResult
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.get_genre_by_id_with_http_info(id, **kwargs)
        else:
            (data) = self.get_genre_by_id_with_http_info(id, **kwargs)
            return data

    def get_genre_by_id_with_http_info(self, id, **kwargs):
        """
        Get genre by id
        Get genre by id
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.get_genre_by_id_with_http_info(id, callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param int id: ID of Genre **(Required)** (required)
        :param int external_station_id: Query on a different (content providing) station *(Optional)*
        :return: GenreResult
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['id', 'external_station_id']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method get_genre_by_id" % key
                )
            params[key] = val
        del params['kwargs']
        # verify the required parameter 'id' is set
        if ('id' not in params) or (params['id'] is None):
            raise ValueError("Missing the required parameter `id` when calling `get_genre_by_id`")

        if 'id' in params and params['id'] < 0:
            raise ValueError("Invalid value for parameter `id` when calling `get_genre_by_id`, must be a value greater than or equal to `0`")

        collection_formats = {}

        path_params = {}
        if 'id' in params:
            path_params['id'] = params['id']

        query_params = []
        if 'external_station_id' in params:
            query_params.append(('_external_station_id', params['external_station_id']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['API Key']

        return self.api_client.call_api('/genres/{id}', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='GenreResult',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)

    def list_genres(self, **kwargs):
        """
        List all genres.
        List all genres.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.list_genres(callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param int page: Current page *(Optional)*
        :param int parent_id: Search on Parent ID of Genre *(Optional)*
        :param int program_id: Search on Program ID *(Optional)* `(Relation)`
        :param int broadcast_id: Search on Broadcast ID *(Optional)* `(Relation)`
        :param int limit: Results per page *(Optional)*
        :param str order_by: Field to order the results *(Optional)*
        :param str order_direction: Direction of ordering *(Optional)*
        :param int external_station_id: Query on a different (content providing) station *(Optional)*
        :return: GenreResults
                 If the method is called asynchronously,
                 returns the request thread.
        """
        kwargs['_return_http_data_only'] = True
        if kwargs.get('callback'):
            return self.list_genres_with_http_info(**kwargs)
        else:
            (data) = self.list_genres_with_http_info(**kwargs)
            return data

    def list_genres_with_http_info(self, **kwargs):
        """
        List all genres.
        List all genres.
        This method makes a synchronous HTTP request by default. To make an
        asynchronous HTTP request, please define a `callback` function
        to be invoked when receiving the response.
        >>> def callback_function(response):
        >>>     pprint(response)
        >>>
        >>> thread = api.list_genres_with_http_info(callback=callback_function)

        :param callback function: The callback function
            for asynchronous request. (optional)
        :param int page: Current page *(Optional)*
        :param int parent_id: Search on Parent ID of Genre *(Optional)*
        :param int program_id: Search on Program ID *(Optional)* `(Relation)`
        :param int broadcast_id: Search on Broadcast ID *(Optional)* `(Relation)`
        :param int limit: Results per page *(Optional)*
        :param str order_by: Field to order the results *(Optional)*
        :param str order_direction: Direction of ordering *(Optional)*
        :param int external_station_id: Query on a different (content providing) station *(Optional)*
        :return: GenreResults
                 If the method is called asynchronously,
                 returns the request thread.
        """

        all_params = ['page', 'parent_id', 'program_id', 'broadcast_id', 'limit', 'order_by', 'order_direction', 'external_station_id']
        all_params.append('callback')
        all_params.append('_return_http_data_only')
        all_params.append('_preload_content')
        all_params.append('_request_timeout')

        params = locals()
        for key, val in iteritems(params['kwargs']):
            if key not in all_params:
                raise TypeError(
                    "Got an unexpected keyword argument '%s'"
                    " to method list_genres" % key
                )
            params[key] = val
        del params['kwargs']

        if 'page' in params and params['page'] < 0:
            raise ValueError("Invalid value for parameter `page` when calling `list_genres`, must be a value greater than or equal to `0`")
        if 'limit' in params and params['limit'] > 50:
            raise ValueError("Invalid value for parameter `limit` when calling `list_genres`, must be a value less than or equal to `50`")
        if 'limit' in params and params['limit'] < 1:
            raise ValueError("Invalid value for parameter `limit` when calling `list_genres`, must be a value greater than or equal to `1`")

        collection_formats = {}

        path_params = {}

        query_params = []
        if 'page' in params:
            query_params.append(('page', params['page']))
        if 'parent_id' in params:
            query_params.append(('parent_id', params['parent_id']))
        if 'program_id' in params:
            query_params.append(('program_id', params['program_id']))
        if 'broadcast_id' in params:
            query_params.append(('broadcast_id', params['broadcast_id']))
        if 'limit' in params:
            query_params.append(('limit', params['limit']))
        if 'order_by' in params:
            query_params.append(('order-by', params['order_by']))
        if 'order_direction' in params:
            query_params.append(('order-direction', params['order_direction']))
        if 'external_station_id' in params:
            query_params.append(('_external_station_id', params['external_station_id']))

        header_params = {}

        form_params = []
        local_var_files = {}

        body_params = None
        # HTTP header `Accept`
        header_params['Accept'] = self.api_client.\
            select_header_accept(['application/json'])

        # HTTP header `Content-Type`
        header_params['Content-Type'] = self.api_client.\
            select_header_content_type(['application/json'])

        # Authentication setting
        auth_settings = ['API Key']

        return self.api_client.call_api('/genres', 'GET',
                                        path_params,
                                        query_params,
                                        header_params,
                                        body=body_params,
                                        post_params=form_params,
                                        files=local_var_files,
                                        response_type='GenreResults',
                                        auth_settings=auth_settings,
                                        callback=params.get('callback'),
                                        _return_http_data_only=params.get('_return_http_data_only'),
                                        _preload_content=params.get('_preload_content', True),
                                        _request_timeout=params.get('_request_timeout'),
                                        collection_formats=collection_formats)
