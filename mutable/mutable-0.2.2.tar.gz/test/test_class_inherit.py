import unittest
import json

from mutable import Mutable

class Child1(Mutable):
    def __init__(self, *args, **kwargs):
        self.a = 0
        Mutable.__init__(self, *args, **kwargs)

class Child2(Mutable):
    def __init__(self, *args, **kwargs):
        Mutable.__init__(self, *args, **kwargs)
        self.a = 0

class TestMutableInherit(unittest.TestCase):

    def test_child_inheritance1(self):
        o = Child1({'a': 1})
        self.assertEqual(o.a, 1)
        self.assertEqual(o.__class__.__name__, 'Child1')

    def test_child_inheritance2(self):
        o = Child2({'a': 1})
        self.assertEqual(o.a, 0)
        self.assertEqual(o.__class__.__name__, 'Child2')

if __name__ == '__main__':
    unittest.main()
