#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    Purpose:
        Swagger Codegen API Methods
'''

__author__ = 'Matt Joyce'
__email__ = 'matt@joyce.nyc'
__copyright__ = 'Copyright 2016, Symphony Communication Services LLC'


import os

from bravado.requests_client import RequestsClient
from bravado.client import SwaggerClient
from bravado.swagger_model import load_file


class SymCodegen():

    def __init__(self):
        mydir = os.path.dirname(os.path.abspath(__file__))
        self.config_path = os.path.join(mydir, '../config/')
        self.rando = 'wat'

    def agent_cg(self, url):
        http_client = RequestsClient()
        self.__url__ = url
        assert http_client
        # load deprecated agent codegen objects from spec
        try:
            agent = SwaggerClient.from_spec(load_file(self.config_path + 'agent-api-public-deprecated.yaml'), config={'also_return_response': True})
            agent.swagger_spec.api_url = self.__url__
        except Exception as err:
            print err
        return agent

    def pod_cg(self, url):
        http_client = RequestsClient()
        self.__url__ = url
        assert http_client
        # load deprecated agent codegen objects from spec
        try:
            pod = SwaggerClient.from_spec(load_file(self.config_path + '/pod-api-public-deprecated.yaml'), config={'also_return_response': True})
            pod.swagger_spec.api_url = self.__url__
        except Exception as err:
            print err
        return pod
