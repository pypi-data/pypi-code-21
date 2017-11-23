import unittest
import json

from mutable import Mutable

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
        self.assertEqual(o["a.b"], 1)

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

    def test_prop_set_value_change_type(self):
        o = Mutable({'a': 1})
        o.a = {'b': {'c': 2}}
        self.assertEqual(o.a.b.c, 2)

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

class TestTypes(unittest.TestCase):

    def test_int(self):
        o = Mutable(1)
        self.assertEqual(o + 1, 2)

    def test_str(self):
        o = Mutable('foo')
        self.assertEqual(o + 'bar', 'foobar')

    def test_list(self):
        o = Mutable(['x', 'y', 'z'])
        self.assertEqual(len(o), 3)
        self.assertEqual(o[0] == 'x', True)
        self.assertEqual(o["0"], 'x')
        self.assertEqual(o[-1], 'z')
        self.assertEqual(o[-2], 'y')
        self.assertEqual(o[1:2][0], 'y')

    def test_list_of_mutables(self):
        o = Mutable({"a": [{"a": 1}, {"b": 2}]})
        self.assertEqual(o.a[0].a, 1)

class TestOps(unittest.TestCase):

    def test_add(self):
        o1 = Mutable({"a" : 1})
        self.assertEqual(o1.a + 2, 3)

    def test_sub(self):
        o1 = Mutable({"a" : 1})
        self.assertEqual(2 - o1.a, 1)

    def test_mul(self):
        o1 = Mutable({"a" : 2})
        self.assertEqual(o1.a * 2, 4)

    def test_div(self):
        o1 = Mutable({"a" : 2})
        self.assertEqual(o1.a / 2, 1)

    def test_deep(self):
        o1 = Mutable({"a": {"b": {"c": 2}}})
        self.assertEqual(o1.a.b.c / 2, 1)
        self.assertEqual(o1.a.b.c * 2, 4)
        self.assertEqual(o1.a.b.c - 1, 1)
        self.assertEqual(o1.a.b.c + 1, 3)

class TestIter(unittest.TestCase):

    def test_list(self):
        o = Mutable(["a", "b", "c"])
        for v in o:
            self.assertEqual(str(v) in 'abc', True)

    def test_dict(self):
        o = Mutable({"a": 1, "b": 2})
        for k, v in o:
            self.assertEqual(k in "ab", True)
            self.assertEqual(v in [1, 2], True)

    def test_dict_with_list_prop(self):
        o = Mutable({"a": ["x", "y", "z"]})
        for k, v in o:
            self.assertEqual(str(k) in "a", True)
        for v in o.a:
            self.assertEqual(str(v) in "xyz", True)

    def test_dict_with_deep_list_prop(self):
        o = Mutable({"a": {"b": {"c": ["x", "y", "z"]}}})
        for v in o.a.b.c:
            self.assertEqual(str(v) in "xyz", True)

if __name__ == "__main__":
    unittest.main()
