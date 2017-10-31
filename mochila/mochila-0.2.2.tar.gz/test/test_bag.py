import unittest
import pytest

import mochila
from test import test_mochila

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class PassThru(Exception):
    pass


def check_pass_thru():
    raise PassThru
    yield 1


class BagTest(test_mochila.MochilaTest, unittest.TestCase):

    type2test = mochila.Bag
    basetype = mochila.Bag

    def setUp(self):
        self.word = word = 'simsalabim'

    def test_init(self):
        # Iterable arg is optional
        self.assertEqual(self.type2test([]), self.type2test())

        a = self.type2test([1, 2, 3])
        b = self.type2test(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

        # Init clears previous values
        a = self.type2test([1, 2, 3])
        a.__init__()
        self.assertEqual(a, self.type2test([]))

        # Init overwrites previous values
        a = self.type2test([1, 2, 3])
        a.__init__([4, 5, 6])
        self.assertEqual(a, self.type2test([4, 5, 6]))

        l = self.type2test()
        self.assertRaises(TypeError, l.__init__, (), 2)
        self.assertRaises(TypeError, l.__init__, (), a=12)

    def test_getitem(self):
        u = self.type2test([0, 1, 2, 3, 4])
        #self.assertRaises(IndexError, u.__getitem__, -len(u) - 1)

    def test_contains(self):
        l = [1, 2, 3]
        u = self.type2test(l)
        for i in l:
            self.assertIn(i, u)
        for i in min(l) - 1, max(l) + 1:
            self.assertNotIn(i, u)

        self.assertRaises(TypeError, u.__contains__)

    def test_contains_fake(self):
        class AllEq:
            # Sequences must use rich comparison against each item
            # (unless "is" is true, or an earlier item answered)
            # So instances of AllEq must be found in all non-empty sequences.
            def __eq__(self, other):
                return True

            __hash__ = None  # Can't meet hash invariant requirements

        self.assertNotIn(AllEq(), self.type2test([]))
        self.assertIn(AllEq(), self.type2test([1]))

    def test_len(self):
        self.assertEqual(len(self.type2test()), 0)
        self.assertEqual(len(self.type2test([])), 0)
        self.assertEqual(len(self.type2test([0])), 1)
        self.assertEqual(len(self.type2test([0, 1, 2])), 3)
        self.assertEqual(len(self.type2test([0, 1, 2, 2])), 4)

    def test_addmul(self):
        u1 = self.type2test([0])
        u2 = self.type2test([0, 1])
        with pytest.raises(TypeError):
            self.assertEqual(u1, u1 + self.type2test())
        with pytest.raises(TypeError):
            self.assertEqual(self.type2test(), u2 * 0)

    def test_iadd(self):
        u = self.type2test([0, 1])
        u += self.type2test()
        self.assertEqual(u, self.type2test([0, 1]))
        u += self.type2test([2, 3])
        self.assertEqual(u, self.type2test([0, 1, 2, 3]))
        u += self.type2test([4, 5])
        self.assertEqual(u, self.type2test([0, 1, 2, 3, 4, 5]))

        u = self.type2test("spam")
        u += self.type2test("eggs")
        self.assertEqual(u, self.type2test("spameggs"))

    def test_count(self):
        a = self.type2test([0, 1, 2]*3)
        self.assertEqual(a.count(0), 3)
        self.assertEqual(a.count(1), 3)
        self.assertEqual(a.count(3), 0)

        self.assertRaises(TypeError, a.count)

        class BadExc(Exception):
            pass

        class BadCmp:
            def __eq__(self, other):
                if other == 2:
                    raise BadExc()
                return False

        self.assertRaises(BadExc, a.count, BadCmp())

    def test_pop(self):
        a = self.type2test([-1, 0, 1])
        e = a.pop()
        self.assertEqual(len(a), 2)
        self.assertTrue(e not in a)
        e = a.pop()
        self.assertEqual(len(a), 1)
        self.assertTrue(e not in a)
        e = a.pop()
        self.assertEqual(a, self.type2test())
        self.assertEqual(len(a), 0)
        self.assertTrue(e not in a)
        self.assertRaises(KeyError, a.pop)

    def test_remove(self):
        a = self.type2test([0, 0, 1])
        a.remove(1)
        self.assertEqual(a, self.type2test([0, 0]))
        a.remove(0)
        self.assertEqual(a, self.type2test([0]))
        a.remove(0)
        self.assertEqual(a, self.type2test([]))
        self.assertRaises(ValueError, a.remove, 0)
        self.assertRaises(TypeError, a.remove)

        class BadExc(Exception):
            pass

        class BadCmp:
            def __eq__(self, other):
                if other == 2:
                    raise BadExc()
                return False

        a = self.type2test([0, 1, 2, 3])
        self.assertRaises(BadExc, a.remove, BadCmp())

        class BadCmp2:
            def __eq__(self, other):
                raise BadExc()

        d = self.type2test('abcdefghcij')
        d.remove('c')
        self.assertEqual(d, self.type2test('abdefghcij'))
        d.remove('c')
        self.assertEqual(d, self.type2test('abdefghij'))
        self.assertRaises(ValueError, d.remove, 'c')
        self.assertEqual(d, self.type2test('abdefghij'))

        # Handle comparison errors
        d = self.type2test(['a', 'b', BadCmp2(), 'c'])
        self.assertRaises(BadExc, d.remove, 'c')

    def test_equals(self):
        self.assertEqual(self.type2test([]), self.type2test())
        b0_3 = self.type2test([0, 1, 2, 3])
        b0_3_bis = self.type2test(list(b0_3))
        self.assertEqual(b0_3, b0_3_bis)
        self.assertTrue(b0_3 is not b0_3_bis)
        self.assertEqual(b0_3, b0_3)
        self.assertFalse(b0_3 == '0123')
        self.assertTrue(self.type2test([]) != '0123')
        self.assertFalse(b0_3 != b0_3)
        b0_4 = self.type2test([0, 1, 2, 3, 4])
        self.assertNotEqual(b0_3, b0_4)
        b1_4 = self.type2test([1, 2, 3, 4])
        self.assertNotEqual(b0_3, b1_4)

    def test_copy(self):
        u = self.type2test([1, 2, 3])
        v = u.copy()
        self.assertEqual(v, self.type2test([1, 2, 3]))

        u = self.type2test([])
        v = u.copy()
        self.assertEqual(v, self.type2test([]))

        # test that it's indeed a copy and not a reference
        u = self.type2test(['a', 'b'])
        v = u.copy()
        v.add('i')
        self.assertTrue('a' in v)
        self.assertTrue('b' in v)
        self.assertTrue('i' in v)
        self.assertFalse('i' in u)

        # test that it's a shallow, not a deep copy
        u = self.type2test([1, 2, [3, 4], 5])
        v = u.copy()
        self.assertEqual(u, v)
        for x in u:
            try:
                if len(x):
                    ux = x
                    break
            except TypeError:
                pass
        for x in v:
            try:
                if len(x):
                    uv = x
                    break
            except TypeError:
                pass
        self.assertIs(ux, uv)
        self.assertRaises(TypeError, u.copy, None)

    def test_sort_by_inplace(self):
        def by_rank(agent):
            return agent.rank

        mochila = self.type2test(test_mochila.agents.values())
        with pytest.warns(UserWarning) as record:
            mochila.sort_by(by_rank, inplace=True)
        # check that only one warning was raised
        self.assertEqual(len(record), 1)
        self.assertEqual(record[0].message.args[0],
                         "You can not sort an unordered Mochila in-place. The operation will be ignored.")

    def test_add_all(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a1.add_all(a2)
        self.assertEqual(len(a1), 3)
        self.assertIn(0, a1)
        self.assertIn(1, a1)
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
