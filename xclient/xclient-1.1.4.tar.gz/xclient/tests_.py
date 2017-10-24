#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import unittest

from xclient import register_xclient, register_xclient2
from xclient.client2 import TradeClient2
from xclient.common import create_raw, sign


class TestTradeClient3(unittest.TestCase):

    def setUp(self):
        import asyncio
        self.loop = asyncio.get_event_loop()
        options = {
            'API_KEY': '1',
            'API_SECRET': '2',
            'API_HOST': 'http://localhost:8000',
            'API_VERSION': '1.0'
        }
        # app_key, app_secret, api_host, api_version = '1', '2', 'http://httpb11in.org', '1.0'
        self.client = register_xclient(options, loop=self.loop)

    def tearDown(self):
        if hasattr(self.client, 'session'):
            self.client.close_session()

    def test_get(self):
        import asyncio
        task1 = asyncio.ensure_future(self.client.get('/drp/customer/remarks/', {}))
        task2 = asyncio.ensure_future(self.client.get('/ab', {}))
        try:
            self.loop.run_until_complete(asyncio.wait([task1, task2]))
            print(task1._result)
        except Exception as e:
            print(e)

    def test_post(self):
        import asyncio
        task1 = asyncio.ensure_future(self.client.post('/drp/customer/remarks/', {'a': 1}))
        task2 = asyncio.ensure_future(self.client.post('/ab1212', {}))
        self.loop.run_until_complete(asyncio.wait([task1, task2]))
        print(task1._result)


class TestTradeClient2(unittest.TestCase):
    def setUp(self):
        options = {
            'API_KEY': '1',
            'API_SECRET': '2',
            'API_HOST': 'http://localhost:8000',
            'API_VERSION': '1.0'
        }
        # app_key, app_secret, api_host, api_version = '1', '2', 'http://httpb11in.org', '1.0'
        self.client = register_xclient2(options)

    def test_get(self):
        content = self.client.get('/login')
        print(content)

    def test_post(self):
        content = self.client.post('/drp/customer/remarks/', {'mobile': 1212})
        print(content)


class TestMD5Sign(unittest.TestCase):
    def test_signature(self):
        params1 = {'customers': [{"c": "中", "b": "MMM"}]}
        secret = 'abcdkaisagroup'
        signature1 = sign(create_raw(params1, secret))
        print(signature1 == '0B3AA4C497078BF926064CEB85EA2177')


class TestRegisterClient(unittest.TestCase):
    def test_client(self):
        options = {
            'API_KEY': 'kdrp',
            'API_SECRET': 'd8912ds89saf',
            'API_HOST': 'http://www.baidu.com',
            'API_VERSION': '1.0'
        }
        client = register_xclient(options)

        if sys.version_info > (3, 5):
            self.assertEqual(client.__class__.__name__ , 'TradeClient3')
        else:
            self.assertEqual(client.__class__.__name__, 'TradeClient2')
