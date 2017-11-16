from __future__ import unicode_literals

import sys
import unittest
from unittest.mock import Mock

from tecplot.tecutil import IndexSet
from tecplot.exception import TecplotTypeError

class TestIndexSet(unittest.TestCase):
    def test___init__(self):
        s = IndexSet()
        self.assertEqual(len(s), 0)
        self.assertEqual(str(s), str(set([])))
        self.assertEqual(repr(s), 'IndexSet()')

        s = IndexSet(1)
        self.assertEqual(len(s), 1)
        self.assertEqual(str(s), str(set([1])))
        self.assertEqual(repr(s), 'IndexSet(1)')

        s = IndexSet(1,2)
        self.assertEqual(len(s), 2)
        for i in [1,2]:
            self.assertIn(i, s)

        def gen():
            for i in range(1,3):
                yield i
        s = IndexSet(gen())
        self.assertEqual(len(s), 2)
        for i in [1,2]:
            self.assertIn(i, s)

        s = IndexSet(*gen())
        self.assertEqual(len(s), 2)
        for i in [1,2]:
            self.assertIn(i, s)

        s = IndexSet(i for i in range(1,3))
        self.assertEqual(len(s), 2)
        for i in [1,2]:
            self.assertIn(i, s)

    def test___repr__(self):
        with IndexSet(1,2) as s1:
            s2 = eval(repr(s1))
            self.assertEqual(s1, s2)

    def test___iter__(self):
        data = [1,2,3]
        s = IndexSet(*data)
        for i in data:
            self.assertIn(i, data)

    def test___iadd__(self):
        s = IndexSet()
        s += [1,2]
        self.assertEqual(len(s), 2)
        for i in [1,2]:
            self.assertIn(i, s)

    def test_context(self):
        with IndexSet() as s:
            s += [1,2]
            self.assertEqual(len(s), 2)
            for i in [1,2]:
                self.assertIn(i, s)

    def test_append(self):
        with IndexSet() as s:
            s.append(1)
            s.append(2)
            self.assertEqual(len(s), 2)
            for i in [1,2]:
                self.assertIn(i, s)
            self.assertRaises(TecplotTypeError, s.append, 'a')

    def test_clear(self):
        with IndexSet(1,2) as s:
            self.assertEqual(len(s), 2)
            s.clear()
            self.assertEqual(len(s), 0)

    def test_large_ints(self):
        with IndexSet(12345) as s:
            self.assertEqual(len(s), 1)
            self.assertEqual(s[0], 12345)

    def test_next(self):
        data = [1,2]
        with IndexSet(*data) as s:
            i = iter(s).next()
            self.assertIn(i, s)
            self.assertIn(i, data)

    def test___eq__(self):
        with IndexSet(1,2,3) as s1:
            with IndexSet(1,2) as s2:
                self.assertFalse(s1 == s2)
                self.assertNotEqual(s1, s2)
                s2.append(3)
                self.assertEqual(s1, s2)
                s2.clear()
                self.assertNotEqual(s1, s2)
                s2 += [1,2,4]
                self.assertFalse(s1 == s2)
                self.assertNotEqual(s1, s2)
                s1.clear()
                s2.clear()
                self.assertEqual(s1, s2)

    def test_index_attr(self):
        class IndexObj(object):
            def __init__(self, i):
                self.index = i

        with IndexSet() as s:
            s.append(IndexObj(1))
            self.assertEqual(s, IndexSet(1))

if __name__ == '__main__':
    from .. import main
    main()
