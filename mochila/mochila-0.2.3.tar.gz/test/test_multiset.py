from collections import Counter
import itertools
import unittest
import pytest

import mochila
from test import test_set_base
from test import test_mochila

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class MultiSetTest(test_set_base.SetTestBase, test_mochila.MochilaTest, unittest.TestCase):

    type2test = mochila.MultiSet
    basetype = mochila.MultiSet

    def test_init(self):
        # Set like init
        s = self.type2test()
        s.__init__(self.word)
        w = set()
        for c in self.word:
            if c not in w:
                w.add(c)
        self.assertEqual(s._items.keys(), w)
        s.__init__(self.otherword)
        w = set()
        for c in self.otherword:
            if c not in w:
                w.add(c)
        self.assertEqual(s._items.keys(), w)
        vals = {'a': 4, 'b': 2}
        s = self.type2test(vals)
        self.assertIn('a', s)
        self.assertIn('b', s)
        self.assertEqual(4, s['a'])
        self.assertEqual(2, s['b'])
        s = self.type2test(a=3, b=5)
        self.assertIn('a', s)
        self.assertIn('b', s)
        self.assertEqual(3, s['a'])
        self.assertEqual(5, s['b'])
        l = self.type2test()
        self.assertRaises(TypeError, l.__init__, (), 2)

    def test_uniquification(self):
        actual = sorted(self.s)
        expected = sorted(self.word)
        self.assertEqual(actual, expected)
        self.assertRaises(test_set_base.PassThru, self.type2test, test_set_base.check_pass_thru())
        self.assertRaises(TypeError, self.type2test, [[]])

    def test_len(self):
        d = Counter(self.word)
        total = sum(d.values())
        self.assertEqual(len(self.s), total)

    def test_addition(self):
        s2 = self.type2test(self.otherword)
        st = self.s + s2
        oracle = self.type2test(Counter(self.word) + Counter(self.otherword))
        self.assertEqual(st, oracle)

    def test_iadd(self):
        s2 = self.type2test(self.otherword)
        self.s += s2
        oracle = self.type2test(Counter(self.word) + Counter(self.otherword))
        self.assertEqual(self.s, oracle)

    def test_sub(self):
        s2 = self.type2test(self.otherword)
        st = self.s - s2
        oracle = self.type2test(Counter(self.word) - Counter(self.otherword))
        self.assertEqual(st, oracle)

    def test_isub(self):
        s2 = self.type2test(self.otherword)
        self.s -= s2
        oracle = self.type2test(Counter(self.word) - Counter(self.otherword))
        self.assertEqual(self.s, oracle)

    def test_lesseq(self):
        s2 = self.type2test('simsalabim')
        self.assertTrue(self.s <= s2)
        s2 = self.type2test('simsalabimsamsim')
        self.assertTrue(self.s <= s2)
        s2 = self.type2test('simsalabum')
        self.assertFalse(s2 <= self.s)

    def test_lessthan(self):
        s2 = self.type2test('simsalabim')
        self.assertFalse(self.s < s2)
        s2 = self.type2test('simsalabimsamsim')
        self.assertTrue(self.s < s2)
        s2 = self.type2test('simsalabum')
        self.assertFalse(s2 < self.s)

    def test_greatereq(self):
        s2 = self.type2test('simsalabim')
        self.assertTrue(s2 >= self.s)
        s2 = self.type2test('simsalabimsamsim')
        self.assertTrue(s2 >= self.s)
        s2 = self.type2test('simsalabum')
        self.assertFalse(self.s >= s2)

    def test_greaterthan(self):
        s2 = self.type2test('simsalabim')
        self.assertFalse(s2 > self.s)
        s2 = self.type2test('simsalabimsamsim')
        self.assertTrue(s2 > self.s)
        s2 = self.type2test('simsalabum')
        self.assertFalse(self.s > s2)

    def test_and(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k in dow:
                k_ = dow[k]
                and_val[k] = v if v <= k_ else k_
        i = self.type2test(and_val)
        self.assertEqual(self.s & self.type2test(self.otherword), i)

    def test_iand(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k in dow:
                k_ = dow[k]
                and_val[k] = v if v <= k_ else k_
        i = self.type2test(and_val)
        self.s &= self.type2test(self.otherword)
        self.assertEqual(self.s, i)

    def test_or(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k in dow:
                k_ = dow[k]
                and_val[k] = v if v >= k_ else k_
            else:
                and_val[k] = v
        for k, v in dow.items():
            if k not in and_val:
                and_val[k] = v
        i = self.type2test(and_val)
        self.assertEqual(self.s | self.type2test(self.otherword), i)

    def test_ior(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k in dow:
                k_ = dow[k]
                and_val[k] = v if v >= k_ else k_
            else:
                and_val[k] = v
        for k, v in dow.items():
            if k not in and_val:
                and_val[k] = v
        i = self.type2test(and_val)
        self.s |= self.type2test(self.otherword)
        self.assertEqual(self.s, i)

    def test_xor(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k not in dow:
                and_val[k] = v
        for k, v in dow.items():
            if k not in dw:
                and_val[k] = v
        i = self.type2test(and_val)
        self.assertEqual(self.s ^ self.type2test(self.otherword), i)

    def test_ixor(self):
        c = list(self.word)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dw = dict(list(x))
        c = list(self.otherword)
        x = zip(c, map(list.count, itertools.repeat(c), c))
        dow = dict(list(x))
        and_val = dict()
        for k, v in dw.items():
            if k not in dow:
                and_val[k] = v
        for k, v in dow.items():
            if k not in dw:
                and_val[k] = v
        i = self.type2test(and_val)
        self.s ^= self.type2test(self.otherword)
        self.assertEqual(self.s, i)

    def test_addmany(self):
        self.s.add('m', 3)
        self.assertEqual(self.s['m'], 5)

    def test_discardmany(self):
        self.s.discard('a', 2)
        self.assertEqual(self.s['a'], 0)
        self.assertNotIn('a', self.s)
        s = self.type2test(self.otherword)
        s.discard('a', 2)
        self.assertEqual(s['a'], 2)

    def test_setOfFrozensets(self):
        t = list(map(frozenset, ['abcdef', 'bbcd', 'bdcb', 'fed', 'fedcba']))
        s = self.type2test(t)
        self.assertEqual(len(s), 5)
        fs = t[0]
        self.assertEqual(s[fs], 2)

    def test_tally(self):
        pass

    def test_add_all(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a1.add_all(a2)
        self.assertEqual(len(a1), 3)
        self.assertTrue(0 in a1)
        self.assertTrue(1 in a1)
        a1 = self.type2test([0, 1, 2])
        a1.add_all(a1)
        self.assertEqual(len(a1), 6)

    def test_remove_all(self):
        a1 = self.type2test([0, 1, 2, 3])
        a2 = self.type2test((1, 3))
        a1.remove_all(a2)
        self.assertEqual(len(a1), 2)
        self.assertNotIn(1, a1)
        self.assertNotIn(3, a1)
        a1 = self.type2test([0, 1, 2, 3])
        a1.remove_all(a1)
        self.assertEqual(len(a1), 0)
        a1 = self.type2test([0, 1, 2, 3])
        a2 = self.type2test((1, 4))
        with pytest.raises(ValueError):
            a1.remove_all(a2)
