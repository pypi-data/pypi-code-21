#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from djdg_core.rest_client import RestClient
from djdg_core.exceptions import StanderResponseError


class TransferStation(object):
    def __init__(self, logger, req_body, token=None, oauth_app_id=None, oauth_app_secret=None):
        """
        :param logger:
        :param req_body: {
            "method":"get",
            "host":"127.0.0.1",
            "path":"/py/v1/deal/deal-info",
            #"protocol":"http",
            #"base_url":"",
            #"params":{},
            #"json":{},
            #"action":"12"
        }
        """
        self.logger = logger
        self.req_body = req_body
        self.client = None
        self.token = token
        self.oauth_app_id = oauth_app_id
        self.oauth_app_secret = oauth_app_secret
        try:
            self.method = self.req_body.pop('method')
            self.path = self.req_body.pop('path')
            self.host = self.req_body.pop('host')
            self.base_url = self.req_body.pop('base_url') if self.req_body.get('base_url', None) else '/'
            self.protocol = self.req_body.pop('protocol') if self.req_body.get('protocol', None) else 'http'

            self.action = self.req_body.pop('action') if self.req_body.get('action', None) else None
            self.json = self.req_body.pop('json') if self.req_body.get('json', None) else None
            self.params = self.req_body.pop('params') if self.req_body.get('params', None) else None

        except Exception as e:
            msg = 'parameters error ,msg is {msg}'.format(
                msg=e.message
            )
            self.logger.info(msg)
            raise StanderResponseError(1, msg=msg)

    def init_client(self, headers=None):
        client = RestClient(
            host=self.host,
            base_url=self.base_url,
            protocol=self.protocol,
            headers=headers,
            logger=self.logger,
            oauth_app_id=self.oauth_app_id,
            oauth_app_secret=self.oauth_app_secret,
        )
        return client

    def get_result(self, client=None):
        if client:
            self.client = client
        else:
            self.client = self.init_client()
        rest_resource = self.client.get_resource(name=self.path, app=None, token=self.token)
        result = rest_resource.do_request(
            self.method,
            action=self.action,
            params=self.params,
            json=self.json,
            raise_exception=True
        )
        return result
