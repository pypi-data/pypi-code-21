#!/usr/bin/python
# -*- coding: utf-8 -*-
import requests

from xclient.common import TradeClient
from xclient.errors import ERROR_ITEMS


class TradeClient2(TradeClient):

    def get(self, path, params=None, request_id=None, session_id=None):
        url = '{}{}'.format(self.api_host, path)
        params, headers = self.build_params_headers(params, request_id, session_id)
        try:
            resp = requests.get(url, params=params, headers=headers)
            return self._parse_resp(resp)
        except requests.exceptions.ConnectionError:
            return False, ERROR_ITEMS.get(404)

    def post(self, path, params=None, request_id=None, session_id=None):
        url = '{}{}'.format(self.api_host, path)
        params, headers = self.build_params_headers(params, request_id, session_id)
        try:
            resp = requests.post(url, data=params, headers=headers)
            return self._parse_resp(resp)
        except requests.exceptions.ConnectionError:
            return False, ERROR_ITEMS.get(404)

    def _parse_resp(self, resp):
        if 300 > resp.status_code >= 200:
            return True, resp.json()
        else:
            return False, ERROR_ITEMS.get(resp.status_code)
