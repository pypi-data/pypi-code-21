#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午3:01
# @Author  : Hou Rong
# @Site    : 
# @File    : HashTest.py
# @Software: PyCharm
import os
import unittest
from toolbox.Hash import *


class TestHash(unittest.TestCase):
    def test_encode(self):
        self.assertEqual(encode('test'), '098f6bcd4621d373cade4e832627b4f6')
        self.assertEqual(encode('test', hasher=hashlib.sha256),
                         '9f86d081884c7d659a2feaa0c55ad015a3bf4f1b2b0b822cd15d6c15b0f00a08')

    def test_file_hash(self):
        path = os.path.dirname(os.path.abspath(__file__))
        self.assertEqual(file_hash(os.path.join(path, 'HashTestFile')), 'f673dd36c99aa9b6aa0e88236956796d')

    def test_token(self):
        self.assertEqual(get_token({'test': 'test'}), '2359cdd9f6124ef769448b8f34c54d65')


if __name__ == '__main__':
    unittest.main()
