import unittest
import json

from src.mutable import Mutable

class TestInit(unittest.TestCase):

    def test_empty_init(self):
        o = Mutable()

    def test_value_init(self):
        o = Mutable('test')
        self.assertEqual(o.__value__, 'test')

    def test_dict_init(self):
        o = Mutable({'a': 1})
        self.assertEqual(o['a'], 1)

    def test_deep_dict_init(self):
        o = Mutable({'a': {'b': 1}})
        self.assertEqual(o['a']['b'], 1)

    def test_json_init(self):
        o = Mutable(json.dumps({'a': {'b': 1}}))
        self.assertEqual(o['a']['b'], 1)

    def test_json_file_init(self):
        o = Mutable('test/test.json')
        self.assertEqual(o['a']['b'], 1)

class TestGet(unittest.TestCase):

    def test_prop_get(self):
        o = Mutable({'a': 1})
        self.assertEqual(o.a, 1)

    def test_prop_get_deep(self):
        o = Mutable({'a': {'b': 1}})
        self.assertEqual(o.a.b, 1)

class TestSet(unittest.TestCase):

    def test_prop_set_value(self):
        o = Mutable({'a': 1})
        o.a = 2
        self.assertEqual(o.a, 2)

    def test_prop_set_dict_value(self):
        o = Mutable({'a': {'b': 1}})
        o.a = {'b': {'c': 2}}
        self.assertEqual(o.a.b.c, 2)
        self.assertEqual(type(o.a), Mutable)

class TestProps(unittest.TestCase):

    def test_props(self):
        o = Mutable({'a': 1, 'b': 2})
        l = [p for p in o.props()]
        self.assertEqual(l[0], 'a')
        self.assertEqual(l[1], 'b')

    def test_deep_props(self):
        o = Mutable({'a': {'b': 1}, 'c': 2})
        l = [p for p in o.props()]
        self.assertEqual(l[0], 'a.b')
        self.assertEqual(l[1], 'c')

if __name__ == '__main__':
    unittest.main()
