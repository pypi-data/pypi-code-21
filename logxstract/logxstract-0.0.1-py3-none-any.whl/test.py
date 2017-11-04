# -*- coding:utf-8 -*-

import os
import unittest
from .lib import extract_xml_from_file


class TestAll(unittest.TestCase):

    def setUp(self):
        self.test_output_file = 'result.txt'
        self.test_input_file = 'sample.log'

    def test_extract(self):
        extract_xml_from_file(
            path='/item',
            body='/item',
            input_file=self.test_input_file,
            output_file=self.test_output_file,
            encoding=None
        )
        self.assertTrue(os.path.exists(self.test_output_file))
        self.assertTrue(bool(os.path.getsize(self.test_output_file)))

    def tearDown(self):
        try:
            os.remove(self.test_output_file)
        except OSError as err:
            print(repr(err))
