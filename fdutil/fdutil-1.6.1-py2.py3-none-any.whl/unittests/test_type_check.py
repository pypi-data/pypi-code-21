import unittest

from fdutil import type_check
from collections import OrderedDict


class TestTypeCheck(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    # is_dictionary
    def test_is_dictionary_true(self):
        self.assertTrue(type_check.is_dictionary({}))

    def test_is_dictionary_true_ordered(self):
        self.assertTrue(type_check.is_dictionary(OrderedDict()))

    def test_is_dictionary_false(self):
        self.assertFalse(type_check.is_dictionary([]))
        self.assertFalse(type_check.is_dictionary(u'text'))

    # is_list
    def test_is_list_true(self):
        self.assertTrue(type_check.is_list([]))

    def test_is_list_false(self):
        self.assertFalse(type_check.is_list({}))
        self.assertFalse(type_check.is_list(u'text'))

    # is_list_or_dictionary
    def test_is_list_or_dictionary_true_list(self):
        self.assertTrue(type_check.is_list_or_dictionary([]))

    def test_is_list_or_dictionary_true_dict(self):
        self.assertTrue(type_check.is_list_or_dictionary({}))

    def test_is_list_or_dictionary_true_dict_ordered(self):
        self.assertTrue(type_check.is_list_or_dictionary(OrderedDict()))

    def test_is_list_or_dictionary_false(self):
        self.assertFalse(type_check.is_list_or_dictionary(u'text'))

    # is_list_of_dictionaries
    def test_is_list_of_dictionaries_true(self):
        self.assertTrue(type_check.is_list_of_dictionaries([{}, {}, {}]))

    def test_is_list_of_dictionaries_false(self):
        self.assertFalse(type_check.is_list_of_dictionaries([{}, {}, {}, 1]))
        self.assertFalse(type_check.is_list_of_dictionaries([]))

    def test_is_list_of_lists_true(self):
        self.assertTrue(type_check.is_list_of_lists([[], [], []]))

    def test_is_list_of_lists_false(self):
        self.assertFalse(type_check.is_list_of_lists([]))
        self.assertFalse(type_check.is_list_of_lists([{}, {}]))
