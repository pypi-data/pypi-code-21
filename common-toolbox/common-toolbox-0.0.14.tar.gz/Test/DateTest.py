#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午5:04
# @Author  : Hou Rong
# @Site    : 
# @File    : DateTest.py
# @Software: PyCharm
import unittest
import toolbox.Date


class TestDate(unittest.TestCase):
    def test_date_range(self):
        toolbox.Date.DATE_FORMAT = '%Y%m%d'
        result = [
            '20170904',
            '20170914',
            '20170924',
            '20171004',
            '20171014',
        ]
        for index, d in enumerate(toolbox.Date.date_range('20170901', '20171011', 10, 3)):
            self.assertEqual(d, result[index])
