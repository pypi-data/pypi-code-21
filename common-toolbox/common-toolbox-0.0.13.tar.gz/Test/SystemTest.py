#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午4:54
# @Author  : Hou Rong
# @Site    : 
# @File    : SystemTest.py
# @Software: PyCharm
import unittest
from toolbox.System import *


class TestSystem(unittest.TestCase):
    def test_get_local_ip_false(self):
        self.assertNotEqual(get_local_ip(), '127.0.0.1')
