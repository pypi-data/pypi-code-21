import unittest

from velenxc.compat import py_str


class CampatTestCase(unittest.TestCase):
    def test_base_str_type_should_be_equal(self):
        self.assertEqual('我们都是牛人', py_str('我们都是牛人'.encode('utf-8')))
