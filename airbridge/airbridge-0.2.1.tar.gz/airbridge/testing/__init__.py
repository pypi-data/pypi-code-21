# -*- coding: utf-8 -*-
from airbridge.testing.config import BaseConfig
from sqlalchemy.sql import text
import unittest
import requests


class AirbridgeBaseTest(unittest.TestCase, BaseConfig):

    def __init__(self, *args, **kwargs):
        unittest.TestCase.__init__(self, *args, **kwargs)
        BaseConfig.__init__(self)
        self.resource = '/'

    def setUp(self):
        print(self.id() + '...............[testing]')

    def tearDown(self):
        print(self.id() + '...............[end]')

    def get_url(self):
        return self.core_host + self.resource

    def send_request(self, url, method='get', headers=None, data=None, cookies=None, allow_redirects=True):
        if headers == None:
            headers = self.headers 

        method = method.lower()

        if method == 'get':
            res = requests.get(url, headers=headers, cookies=cookies, allow_redirects=allow_redirects)
        elif method == 'post':
            res = requests.post(url, data=data, headers=headers, cookies=cookies)
        elif method == 'put':
            res = requests.put(url, data=data, headers=headers, cookies=cookies)
        elif method == 'delete':
            res = requests.delete(url, data=data, headers=headers, cookies=cookies)
        else:
            print 'Now allowed method'

        return res

    def check_api_response(self, res, expected=200):
        err_msg = """Expected {0}. But we got wrong status code: {1}\nError message:\n{2}""".format(str(expected), str(res.status_code), res.text.encode('utf-8'))
        self.assertEqual(res.status_code, expected, err_msg)

        if res.status_code == expected:
            print """Test was successful. Response text below:\n{0}""".format(res.text.encode('utf-8'))
