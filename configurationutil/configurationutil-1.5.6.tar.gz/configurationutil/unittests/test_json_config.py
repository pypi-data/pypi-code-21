import json
import unittest

import os

from configurationutil.cfg_providers import json_provider
from fdutil.path_tools import pop_path

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


class TestJSONConfig(unittest.TestCase):

    def setUp(self):
        self.cfg_file = os.path.join(pop_path(__file__), u'test_json_config.json')

        self.config = json_provider.JSONConfig(config_file=self.cfg_file,
                                               create=True)

        self.test_config = {
            u'test': 123,
            u'test2': 456,
            u'test3': 789,
            u'test5': {
                u'item1': u'abc',
                u'item2': 999,
                u'item3': [u'def', 888],
                u'item4': {
                    u'a': 987,
                    u'b': u'xyz'
                },
                u'nested-get.test.com': {
                    u'c': 3,
                    u'd': 4
                }
            },
            u'get.test.com': u'get dot key'
        }

        self.config.cfg = self.test_config.copy()
        self.config.save()

    def tearDown(self):
        try:
            os.remove(self.cfg_file)

        except OSError:
            pass

    # Instantiation
    def test_instantiation(self):
        self.assertEqual(self.config.cfg.get(u'test'), 123,
                         u'JSONConfig instantiation failed')

        self.assertEqual(self.config.get(u'test'), 123,
                         u'JSONConfig instantiation failed')

    def test_instantiation_invalid_config_file(self):
        with self.assertRaises(IOError):
            self.cfg_test = json_provider.JSONConfig(config_file=u'does_not_exist!')

    def test_instantiation_default(self):
        self.cfg_file = os.path.join(pop_path(__file__), u'test_json_config_default.json')

        self.config = json_provider.JSONConfig(config_file=self.cfg_file,
                                               create=True)

        self.assertEqual(self.config.cfg, {},
                         u'JSONConfig default instantiation failed')

    def test_instantiation_missing_default(self):

        default_template = json_provider.JSONConfig.DEFAULT_TEMPLATE
        del json_provider.JSONConfig.DEFAULT_TEMPLATE

        self.cfg_file = os.path.join(pop_path(__file__), u'test_json_config_missing_default.json')

        with self.assertRaises(NotImplementedError):
            self.config = json_provider.JSONConfig(config_file=self.cfg_file,
                                                   create=True)

        json_provider.JSONConfig.DEFAULT_TEMPLATE = default_template

    # Save
    def test_save(self):
        self.assertFalse(u'test4' in self.config)

        self.config.cfg[u'test4'] = u'it worked!'

        f = json.load(open(self.cfg_file))
        self.assertFalse(u'test4' in f)
        self.assertTrue(u'test4' in self.config)

        self.config.save()

        f = json.load(open(self.cfg_file))
        self.assertTrue(u'test4' in f)
        self.assertTrue(u'test4' in self.config)

    # Find
    def test_find(self):

        msg = u'Find failed'

        filters = [(999, None)]
        filters2 = [(999, None), (u'abc', None, u'OR')]
        filters3 = [(u'a', 987), (u'abc', None, u'OR')]

        expected_item4 = {
            u'a': 987,
            u'b': u'xyz'
        }

        self.assertEqual(self.config.find(u'test5', filters), {u'item2': 999}, msg)
        self.assertEqual(self.config.find(u'test5', filters2), {u'item1': u'abc', u'item2': 999}, msg)
        self.assertEqual(self.config.find(u'test5', filters3), {u'item1': u'abc', u'item4': expected_item4}, msg)

    def test_find_multi_item(self):

        filters = [(987, None)]

        self.assertEqual(self.config.find(u'test5.item4', filters), {u'a': 987}, u'Find multi item failed')

    def test_find_no_filters(self):
        self.assertEqual(self.config.find(u'test5'), self.test_config.get(u'test5'), u'Find no filters failed')

    def test_find_no_filters_multi_item(self):
        self.assertEqual(self.config.find(u'test5.item4'), self.test_config.get(u'test5').get(u'item4'),
                         u'Find no filters multi item failed')

    def test_find_no_key(self):

        msg = u'Find no key failed'

        filters = [(123, None)]
        filters2 = [(123, None), (456, None, u'OR')]
        filters3 = [(u'item2', 999), (456, None, u'OR')]

        expected_test5 = self.test_config.get(u'test5')

        self.assertEqual(self.config.find(filters=filters), {u'test': 123}, msg)
        self.assertEqual(self.config.find(filters=filters2), {u'test': 123, u'test2': 456}, msg)
        self.assertEqual(self.config.find(filters=filters3), {u'test2': 456, u'test5': expected_test5}, msg)

    def test_find_invalid_key(self):

        filters = [(123, None)]

        with self.assertRaises(KeyError):
            self.config.find(u'test2', filters)

    def test_find_invalid_key_multi_item(self):

        filters = [(999, None)]

        with self.assertRaises(KeyError):
            self.config.find(u'test5.item2', filters)

    # Getter
    def test_get(self):
        self.assertEqual(self.config[u'test3'], 789, u'Get failed')

    def test_get_multi_item(self):

        msg = u'Get multi failed'

        self.assertEqual(self.config[u'test5.item1'], u'abc', msg)
        self.assertEqual(self.config[u'test5.item2'], 999, msg)
        self.assertEqual(self.config[u'test5.item3'], [u'def', 888],  msg)
        self.assertEqual(self.config[u'test5.item4'], {u'a': 987, u'b': u'xyz'}, msg)
        self.assertEqual(self.config[u'test5.item4.a'], 987, msg)
        self.assertEqual(self.config[u'test5.item4.b'], u'xyz', msg)

    def test_get_full_cfg(self):
        self.assertEqual(self.config.cfg, self.test_config, u'Get full config failed')

    def test_get_missing_item(self):
        with self.assertRaises(KeyError):
            _ = self.config[u'not_here']

    def test_get_missing_multi_item(self):
        with self.assertRaises(KeyError):
            _ = self.config[u'test5.not_here']

        with self.assertRaises(KeyError):
            _ = self.config[u'test5.item4.not_here']

    def test_get_dot_key(self):
        self.assertEqual(self.config[u'get.test.com'], u'get dot key', u'Get dot key failed')

    def test_get_multi_item_dot_key(self):
        expected_output = self.test_config[u'test5'][u'nested-get.test.com']

        self.assertEqual(self.config[u'test5.nested-get.test.com'], expected_output, u'Get multi dot key failed')

    # Setter
    def test_set_new_item(self):
        self.assertFalse(u'test_set' in self.config)

        self.config[u'test_set'] = u'Set some config'

        self.assertEqual(self.config[u'test_set'], u'Set some config', u'Set new value failed')

    def test_set_new_multi_item(self):
        self.assertFalse(u'test5.item5' in self.config)
        self.assertTrue(u'test5.item4' in self.config)
        self.assertFalse(u'test5.item4.c' in self.config)

        msg = u'Set new multi item failed'

        test_value = u'Set multi item config'
        test_value2 = u'Set multi item config 2'

        self.config[u'test5.item5'] = test_value
        self.config[u'test5.item4.c'] = test_value2

        self.assertEqual(self.config[u'test5.item5'], test_value, msg)
        self.assertEqual(self.config[u'test5.item4.c'], test_value2, msg)

    def test_set_update_existing_item(self):
        self.assertTrue(u'test2' in self.config)
        self.assertEqual(self.config[u'test2'], 456)

        self.config[u'test2'] = 555

        self.assertEqual(self.config[u'test2'], 555, u'Set update existing value failed')

    def test_set_update_existing_multi_item(self):
        self.assertTrue(u'test5.item1' in self.config)
        self.assertEqual(self.config[u'test5.item1'], u'abc')
        self.assertTrue(u'test5.item4' in self.config)
        self.assertTrue(u'test5.item4.a' in self.config)
        self.assertEqual(self.config[u'test5.item4.a'], 987)

        msg = u'Set update existing multi value failed'

        test_value = 666
        test_value2 = 777

        self.config[u'test5.item1'] = test_value
        self.config[u'test5.item4.a'] = test_value2

        self.assertEqual(self.config[u'test5.item1'], test_value, msg)
        self.assertEqual(self.config[u'test5.item4.a'], test_value2, msg)

    def test_set_new_item_dot_key(self):
        self.assertFalse(u'www.example.com' in self.config.cfg)

        self.config[u'www.example.com'] = u'Set some config'

        self.assertEqual(self.config.cfg[u'www.example.com'], u'Set some config',
                         u'Set an object key that has dots in (i.e url) failed')

        data = {
            u'a': 1,
            u'b': 2
        }

        self.config[u'10.10.10.1'] = data

        self.assertEqual(self.config.cfg[u'10.10.10.1'], data,
                         u'Set an object key that has dots in (i.e url) failed')

    def test_set_new_multi_item_dot_key(self):
        self.assertFalse(u'www.example.com' in self.config.cfg)

        self.config[u'test5.www.example.com'] = u'Set nested dot config'

        self.assertEqual(self.config.cfg.get(u'test5')[u'www.example.com'], u'Set nested dot config',
                         u'Set a nested object key that has dots in (i.e url) failed')

        data = {
            u'a': 1,
            u'b': 2
        }

        self.config[u'test5.10.10.10.2'] = data

        self.assertEqual(self.config.cfg.get(u'test5')[u'10.10.10.2'], data,
                         u'Set a nested object key that has dots in (i.e url) failed')

    # Deleter
    def test_del(self):
        self.config[u'test_del'] = u'Del some config'

        self.assertTrue(u'test_del' in self.config)

        del self.config[u'test_del']

        self.assertFalse(u'test_del' in self.config)

    def test_del_multi_item(self):
        self.config[u'test5.item6'] = u'Del some config'
        self.config[u'test5.item4.d'] = u'Del some more config'

        self.assertTrue(u'test5.item6' in self.config)
        self.assertTrue(u'test5.item4.d' in self.config)

        del self.config[u'test5.item6']
        del self.config[u'test5.item4.d']

        self.assertFalse(u'test5.item6' in self.config)
        self.assertFalse(u'test5.item4.d' in self.config)

    def test_del_invalid_item(self):
        self.assertFalse(u'test_del' in self.config)

        with self.assertRaises(KeyError):
            del self.config[u'test_del']

    def test_del_invalid_multi_item(self):
        self.assertFalse(u'test5.item6' in self.config)
        self.assertFalse(u'test5.item4.d' in self.config)

        with self.assertRaises(KeyError):
            del self.config[u'test5.item6']

        with self.assertRaises(KeyError):
            del self.config[u'test5.item4.d']

    def test_del_dot_key(self):
        self.config.cfg[u'del.test.com'] = u'Del some config'

        self.assertTrue(u'del.test.com' in self.config.cfg)

        del self.config[u'del.test.com']

        self.assertFalse(u'del.test.com' in self.config.cfg)

    def test_del_multi_item_dot_key(self):
        self.config.cfg[u'test5'][u'del2.test.com'] = u'Del some config'

        self.assertTrue(u'del2.test.com' in self.config.cfg[u'test5'])

        del self.config[u'test5.del2.test.com']

        self.assertFalse(u'del2.test.com' in self.config.cfg[u'test5'])

    # Iterator
    def test_iter_item(self):
        self.assertTrue(u'test2' in self.config)
        self.assertFalse(u'test6' in self.config)

    def test_iter_multi_item(self):
        self.assertTrue(u'test5.item1' in self.config)
        self.assertFalse(u'test5.item5' in self.config)
        self.assertTrue(u'test5.item4.a' in self.config)
        self.assertFalse(u'test5.item4.c' in self.config)

    # Length
    def test_len_item(self):
        self.assertEqual(len(self.config), 5)

    def test_len_multi_item(self):
        self.assertEqual(len(self.config[u'test5']), 5)
        self.assertEqual(len(self.config[u'test5.item4']), 2)

if __name__ == u'__main__':
    unittest.main()
