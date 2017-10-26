#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:27
# @Author  : Hou Rong
# @Site    : 
# @File    : WebTest.py
# @Software: PyCharm
import unittest
from toolbox.Web import *


class TestWeb(unittest.TestCase):
    def test_soap_body(self):
        @soap_body(soap_action='HelloWorld')
        def hello_world():
            return 'Hello World'

        self.assertEqual(hello_world(),
                         '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
                         '<soap:Header/><soap:Body><HelloWorld versionNumber="7.0">Hello World'
                         '</HelloWorld></soap:Body></soap:Envelope>')

    def test_modify_url(self):
        self.assertEqual(
            modify_url(
                'https://ihg.scene7.com/is/image/ihg/transparent_1440?fmt=png-alpha&wid=668&hei=385#asdfasdf#123123'),
            'https://ihg.scene7.com/is/image/ihg/transparent_1440?fmt=png-alpha&wid=668&hei=385')

    def test_modify_url_2(self):
        self.assertEqual(
            modify_url('asdfasdfasdfasdf'), ''
        )
