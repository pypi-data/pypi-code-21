# -*- coding: utf-8 -*-
import unittest

from pynlple.utils import DictionaryHelper


class DictionaryHelperTest(unittest.TestCase):
    """"""""

    def setUp(self):
        self.data = {'key': 'value',
                     'none_key': None,
                     'list_key': ['list_value1', 'list_value2'],
                     'dict_key': {'dict_dict_key': 'dict_dict_value', 'dict_dict_key2': 'dict_dict_value'},
                     'dict_key2': {'dict_list_key': ['dict_list_value', 'dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']},
                     'dict_key3': {'dict_dict_key': {'dict_dict_dict_key': 'dict_dict_dict_value', 'dict_dict_dict_key2': 'dict_dict_dict_value'}, 'dict_dict_key2': {'dict_dict_dict_key': 'dict_dict_dict_value'}}
                     }
        self.data2 = {
            10: 15,
            20: 30,
            -10: -40
        }

    def test_should_match_key(self):
        condition = {'key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_empty_key(self):
        condition = {}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_none_key_None_value(self):
        condition = {'none_key': None}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_none_key_empty_value(self):
        condition = {'none_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_list_key(self):
        condition = ['key', 'list_key']
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key(self):
        condition = {'dict_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_None_key(self):
        condition = None
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_key_None_value(self):
        condition = {'key': None}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_key_value(self):
        condition = {'key': 'value'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_wrong_key(self):
        condition = {'not_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_key_extra_value(self):
        condition = {'key': ['value', 'value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_wrong_key_None_value(self):
        condition = {'not_key': None}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_key_wrong_value(self):
        condition = {'key': 'not_value'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_wrong_key_value(self):
        condition = {'not_key': 'value'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_list_key_first_value(self):
        condition = {'list_key': 'list_value1'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_list_key_all_values(self):
        condition = {'list_key': ['list_value1', 'list_value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_list_key_right_and_wrong_values(self):
        condition = {'list_key': ['list_value1', 'not_list_value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_list_key_wrong_and_right_values(self):
        condition = {'list_key': ['not_list_value1', 'list_value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_dict_key_dict_dict_key(self):
        condition = {'dict_key': 'dict_dict_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_dict_key_wrong_dict_dict_key(self):
        condition = {'dict_key': 'not_dict_dict_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_dict_key_dict_dict_all_keys(self):
        condition = {'dict_key': ['dict_dict_key', 'dict_dict_key2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key_dict_dict_all_tuple_keys(self):
        condition = {'dict_key': ('dict_dict_key', 'dict_dict_key2')}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key_dict_dict_all_tuple_keys_and_value(self):
        condition = {'dict_key': ('dict_dict_key', {'dict_dict_key2': 'dict_dict_value'})}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_dict_key_dict_dict_tuple_wrong_keys(self):
        condition = {'dict_key': ('dict_dict_key', 'not_dict_dict_key2')}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_dict_key_dict_dict_all_tuple_keys_and_wrong_value(self):
        condition = {'dict_key': ('dict_dict_key', {'dict_dict_key2': 'not_dict_dict_value'})}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_dict_key_dict_dict_partially_wrong_keys(self):
        condition = {'dict_key': ['not_dict_dict_key', 'dict_dict_key2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_dict_key_dict_dict_partially_wrong_keys_2(self):
        condition = {'dict_key': ['dict_dict_key', 'not_dict_dict_key2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_dict_key_dict_list_key(self):
        condition = {'dict_key2': 'dict_list_key'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key_dict_list_keys(self):
        condition = {'dict_key2': ['dict_list_key', 'dict_list_key2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key_dict_list_key_dict_list_value(self):
        condition = {'dict_key2': {'dict_list_key': 'dict_list_value'}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_key_dict_list_key_dict_list_values(self):
        condition = {'dict_key2': {'dict_list_key': ['dict_list_value', 'dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_dict_key_dict_list_key_dict_list_partially_wrong_values(self):
        condition = {'dict_key2': {'dict_list_key': ['dict_list_value', 'not_dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_dict_key_dict_list_key_dict_list_partially_wrong_values2(self):
        condition = {'dict_key2': {'dict_list_key': ['not_dict_list_value', 'dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_dict_key_dict_list_partially_wrong_keys(self):
        condition = {'dict_key2': ['dict_list_key', 'not_dict_list_key2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_identical_sub_keys_and_values(self):
        condition = {'dict_key2': {'dict_list_key': ['dict_list_value', 'dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_almost_identical_keys_and_values(self):
        condition = {'dict_key2': {'dict_list_key': ['dict_list_value', 'not_dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_almost_identical_keys_and_values2(self):
        condition = {'dict_key2': ['dict_list_key', {'dict_list_key2': ['dict_list_value', 'not_dict_list_value2']}]}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_not_match_almost_identical_keys_and_values3(self):
        condition = {'dict_key2': {'not_dict_list_key': ['dict_list_value', 'dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_dict_dict_dict_key(self):
        condition = {'dict_key3': {'dict_dict_key': 'dict_dict_dict_key'}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_dict_dict_keys(self):
        condition = {'dict_key3': {'dict_dict_key': ['dict_dict_dict_key', 'dict_dict_dict_key2']}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_dict_dict_keys_and_one_value(self):
        condition = {'dict_key3': {'dict_dict_key': ['dict_dict_dict_key', {'dict_dict_dict_key2': 'dict_dict_dict_value'}]}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_dict_dict_dict_keys_and_one_value_and_dict_dict_key_and_dict_dict_dict_key(self):
        condition = {'dict_key3': {'dict_dict_key': ['dict_dict_dict_key', {'dict_dict_dict_key2': 'dict_dict_dict_value'}], 'dict_dict_key2': 'dict_dict_dict_key'}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_identical_full_keys_and_values(self):
        condition = {'key': 'value',
                     'list_key': ['list_value1', 'list_value2'],
                     'dict_key': {'dict_dict_key': 'dict_dict_value', 'dict_dict_key2': 'dict_dict_value'},
                     'dict_key2': {'dict_list_key': ['dict_list_value', 'dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']},
                     'dict_key3': {'dict_dict_key': {'dict_dict_dict_key': 'dict_dict_dict_value', 'dict_dict_dict_key2': 'dict_dict_dict_value'}, 'dict_dict_key2': {'dict_dict_dict_key': 'dict_dict_dict_value'}}
                     }
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_identical_full_keys_and_values_but_with_extra_field(self):
        condition = {'extra_key': None,
                     'key': 'value',
                     'list_key': ['list_value1', 'list_value2'],
                     'dict_key': {'dict_dict_key': 'dict_dict_value', 'dict_dict_key2': 'dict_dict_value'},
                     'dict_key2': {'dict_list_key': ['dict_list_value', 'dict_list_value2'], 'dict_list_key2': ['dict_list_value', 'dict_list_value2']},
                     'dict_key3': {'dict_dict_key': {'dict_dict_dict_key': 'dict_dict_dict_value', 'dict_dict_dict_key2': 'dict_dict_dict_value'}, 'dict_dict_key2': {'dict_dict_dict_key': 'dict_dict_dict_value'}}
                     }
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_integer_key(self):
        condition = {10}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertTrue(matches)

    def test_should_match_integer_negative_key(self):
        condition = {-10}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertTrue(matches)

    def test_should_not_match_integer_wrong_key(self):
        condition = {15}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertFalse(matches)

    def test_should_match_integer_key_and_value(self):
        condition = {10: 15}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertTrue(matches)

    def test_should_match_integer_keys_and_values(self):
        condition = {10: 15, 20: 30}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertTrue(matches)

    def test_should_not_match_integer_key_and_wrong_value(self):
        condition = {10: 16}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertFalse(matches)

    def test_should_not_match_integer_keys_and_partially_wrong_values(self):
        condition = {10: 15, 20: 40}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertFalse(matches)

    def test_should_match_with_function_condition(self):
        condition = {10: lambda x: x < 20}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertTrue(matches)

    def test_should_not_match_with_function_condition(self):
        condition = {10: lambda x: x < 10}
        matches = DictionaryHelper.matches(condition, self.data2)
        self.assertFalse(matches)

    def test_should_match_with_function_string_equals_condition(self):
        condition = {'key': lambda x: x == 'value'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_with_function_string_not_equals_condition(self):
        condition = {'key': lambda x: x == 'value2'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_with_function_string_contains_condition(self):
        condition = {'key': lambda x: 'v' in x and 'x' not in x}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_with_function_long_key_path(self):
        condition = {'dict_key3': {'dict_dict_key': lambda x: 'dict_dict_dict_key' in x}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_with_function_long_key_path_simple_condition(self):
        condition = {'dict_key3': {'dict_dict_key': lambda x: len(x) > 1}}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_with_function_simple_condition_coupled_default_condition(self):
        condition = {'key': (lambda x: 'v' in x and 'x' not in x, 'value')}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_match_with_function_simple_condition_added_default_condition(self):
        condition = {'key': lambda x: 'v' in x}, {'key': 'value'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_with_function_simple_condition_added_default_fault_condition(self):
        condition = {'key': lambda x: 'v' in x}, {'key': 'value2'}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

    def test_should_match_with_function_complex_condition(self):
        condition = {'list_key': lambda x: x == ['list_value1', 'list_value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertTrue(matches)

    def test_should_not_match_with_function_complex_condition(self):
        condition = {'list_key': lambda x: x == ['list_value3', 'list_value2']}
        matches = DictionaryHelper.matches(condition, self.data)
        self.assertFalse(matches)

if __name__ == '__main__':
    unittest.main()
