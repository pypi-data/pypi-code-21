#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2017/8/1 下午5:27
# @Author  : Hou Rong
# @Site    : 
# @File    : ImageTest.py
# @Software: PyCharm
import os
import unittest
from toolbox.Image import *


class TestImageIsCompleteScaleOk(unittest.TestCase):
    path = os.path.dirname(os.path.abspath(__file__))
    text_file = os.path.join(path, 'HashTestFile')
    img_file = os.path.join(path, 'ImageTestFile.jpeg')

    def test_is_not_image(self):
        e_code, x, y = is_complete_scale_ok(self.text_file)
        self.assertEqual(e_code, 1)

    def test_is_image(self):
        e_code, x, y = is_complete_scale_ok(self.img_file)
        self.assertEqual(e_code, 0)

    def test_is_image_correct_size(self):
        e_code, h, w = is_complete_scale_ok(self.img_file)
        self.assertEqual(h, 600)
        self.assertEqual(w, 800)

    def test_min_pixels(self):
        e_code, h, w = is_complete_scale_ok(self.img_file, min_sum_pixels=500000)
        self.assertEqual(e_code, 3)

    def test_wrong_scale(self):
        e_code, h, w = is_complete_scale_ok(self.img_file, max_scale=1)
        self.assertEqual(e_code, 5)
