#!/usr/bin/python
# -*- coding: utf-8 -*-
import aiohttp

from xclient.common import TradeClient
from xclient.errors import ERROR_ITEMS, XClientError


class TradeClient3(TradeClient):

    def __init__(self, app_key, app_secret, api_host, api_version, loop=None):
        super(TradeClient3, self).__init__(app_key, app_secret, api_host, api_version)
        self.session = aiohttp.ClientSession(loop=loop)

    async def get(self, path, params=None, request_id=None, session_id=None):
        url = '{}{}'.format(self.api_host, path)
        params, headers = self.build_params_headers(params, request_id, session_id)

        try:
            async with self.session.get(url, params=params, headers=headers) as resp:
                data = await self._parse_resp(resp)
                return data
        except aiohttp.ClientConnectorError:
            raise XClientError(404)

    async def post(self, path, params=None, request_id=None, session_id=None):
        url = '{}{}'.format(self.api_host, path)
        params, headers = self.build_params_headers(params, request_id, session_id)

        try:
            async with self.session.post(url, data=params, headers=headers) as resp:
                data = await self._parse_resp(resp)
                return data
        except aiohttp.ClientConnectorError:
            raise XClientError(404)

    async def _parse_resp(self, resp):
        status_code = resp.status
        if 300 > status_code >= 200:
            return True, await resp.json()
        else:
            return False, ERROR_ITEMS.get(status_code)

    def __del__(self):
        self.session.close()
