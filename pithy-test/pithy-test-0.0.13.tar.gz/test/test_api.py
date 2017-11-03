#!/usr/bin/python
# coding=utf-8
from pithy import request
import unittest


class DemoAPP(object):

    def __init__(self):
        self.base_url = 'http://httpbin.org/'
        self.headers = {
            'b': 'asdf'
        }

    @request(url='get')
    def get(self, value):
        params = {
            'key': value
        }
        return dict(params=params)


class TestApi(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = DemoAPP()

    def test_get(self):
        res = self.app.get(123)
        print res.get_params()
        res.json
        res.content
