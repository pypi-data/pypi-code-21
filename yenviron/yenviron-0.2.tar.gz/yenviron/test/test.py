import os
import unittest

from .. import Yenviron
from .. import exceptions
from ..yenviron import yenviron_read


TEST_FILE = os.path.join(os.path.dirname(__file__), 'yenviron.yml')


class YenvironTests(unittest.TestCase):

    def setUp(self):
        self.yenv = yenviron_read(TEST_FILE)

    def test_constructor_no_dictionary(self):
        with self.assertRaises(exceptions.YenvironError):
            Yenviron(1)

    def test_constructor(self):
        Yenviron({})

    def test_getitem_integer(self):
        self.assertIsInstance(self.yenv['INTEGER_1'], int)
        self.assertIsInstance(self.yenv.get('INTEGER_1'), int)
        self.assertIsInstance(self.yenv.get('INTEGER_314', 1), int)

    def test_getitem_string(self):
        self.assertIsInstance(self.yenv['STRING_1'], str)
        self.assertIsInstance(self.yenv.get('STRING_1'), str)
        self.assertIsInstance(self.yenv.get('STRING_314', 'a'), str)

    def test_getitem_list(self):
        self.assertIsInstance(self.yenv['LIST_INTEGER'], list)
        self.assertIsInstance(self.yenv.get('LIST_INTEGER'), list)
        self.assertIsInstance(self.yenv.get('LIST_INTEGER_314', []), list)

    def test_getitem_dict(self):
        self.assertIsInstance(self.yenv['DICTIONARY'], dict)
        self.assertIsInstance(self.yenv.get('DICTIONARY'), dict)
        self.assertIsInstance(self.yenv.get('DICTIONARY_314', {}), dict)

    def test_getitem_missing(self):
        with self.assertRaises(exceptions.YenvironKeyError):
            value = self.yenv['DICTIONARY_314']

    def test_setitem(self):
        with self.assertRaises(TypeError):
            self.yenv['ANY_VALUE'] = 1

    def test_delitem(self):
        with self.assertRaises(TypeError):
            del self.yenv['ANY_VALUE']

    def test_contains(self):
        self.assertTrue('INTEGER_1' in self.yenv)
        self.assertFalse('INTEGER_314' in self.yenv)
