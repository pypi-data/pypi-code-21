# -*- coding: utf-8 -*-

from requests.auth import AuthBase
from tapioca import (JSONAdapterMixin, TapiocaAdapter,
                     generate_wrapper_from_adapter)

from .resource_mapping import RESOURCE_MAPPING


class HTTPTokenAuth(AuthBase):

    def __init__(self, token):
        self.token = token

    def __call__(self, request):
        request.headers['Authorization'] = 'Token {0}'.format(self.token)

        return request


class CloudezClientAdapter(JSONAdapterMixin, TapiocaAdapter):
    api_root = 'https://api.cloudez.io/v0/'
    resource_mapping = RESOURCE_MAPPING

    def get_api_root(self, api_params):
        api_root = api_params.get('api_root')

        if api_root:
            return api_root
        else:
            return self.api_root

    def get_request_kwargs(self, api_params, *args, **kwargs):
        params = super(CloudezClientAdapter, self).get_request_kwargs(
            api_params, *args, **kwargs)

        params['auth'] = HTTPTokenAuth(api_params.get('auth_token'))

        return params

    def get_iterator_list(self, response_data):
        return response_data

    def get_iterator_next_request_kwargs(self, iterator_request_kwargs,
                                         response_data, response):
        pass


Cloudez = generate_wrapper_from_adapter(CloudezClientAdapter)
