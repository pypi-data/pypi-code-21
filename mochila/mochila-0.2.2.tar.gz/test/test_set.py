import unittest
import pytest
import weakref

import mochila
from test import test_set_base
from test import test_mochila

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class PassThru(Exception):
    pass


def check_pass_thru():
    raise PassThru
    yield 1


class SetTest(test_set_base.SetTestBase, test_mochila.MochilaTest, unittest.TestCase):

    type2test = mochila.Set
    basetype = mochila.Set

    def test_init(self):
        s = self.type2test()
        s.__init__(self.word)
        self.assertEqual(s._items, set(self.word))
        s.__init__(self.otherword)
        self.assertEqual(s._items, set(self.otherword))

        a = self.type2test([1, 2, 3])
        b = self.type2test(a)
        self.assertNotEqual(id(a), id(b))
        self.assertEqual(a, b)

        # FIXME need to test that args and kwargs can be passed
        self.assertRaises(TypeError, s.__init__, s, 2)
        self.assertRaises(TypeError, s.__init__, a=1)

    def test_constructor_identity(self):
        s = self.type2test(range(3))
        t = self.type2test(s)
        self.assertNotEqual(id(s), id(t))

    def test_hash(self):
        self.assertRaises(TypeError, hash, self.s)

    def test_clear(self):
        self.s.clear()
        self.assertEqual(self.s, self.type2test())
        self.assertEqual(len(self.s), 0)

    def test_copy(self):
        dup = self.s.copy()
        self.assertEqual(self.s, dup)
        self.assertNotEqual(id(self.s), id(dup))
        self.assertEqual(type(dup), self.basetype)

    def test_add(self):
        self.s.add('Q')
        self.assertIn('Q', self.s)
        dup = self.s.copy()
        self.s.add('Q')
        self.assertEqual(self.s, dup)
        self.assertRaises(TypeError, self.s.add, [])

    def test_remove(self):
        self.s.remove('a')
        self.assertNotIn('a', self.s)
        self.assertRaises(KeyError, self.s.remove, 'Q')
        self.assertRaises(TypeError, self.s.remove, [])

    def test_discard(self):
        self.s.discard('a')
        self.assertNotIn('a', self.s)
        self.s.discard('Q')
        self.assertRaises(TypeError, self.s.discard, [])

    def test_pop(self):
        for i in range(len(self.s)):
            elem = self.s.pop()
            self.assertNotIn(elem, self.s)
        self.assertRaises(KeyError, self.s.pop)

    def test_ior(self):
        self.s |= set(self.otherword)
        for c in (self.word + self.otherword):
            self.assertIn(c, self.s)

    def test_iand(self):
        self.s &= set(self.otherword)
        for c in (self.word + self.otherword):
            if c in self.otherword and c in self.word:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

    def test_isub(self):
        self.s -= set(self.otherword)
        for c in (self.word + self.otherword):
            if c in self.word and c not in self.otherword:
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

    def test_ixor(self):
        self.s ^= set(self.otherword)
        for c in (self.word + self.otherword):
            if (c in self.word) ^ (c in self.otherword):
                self.assertIn(c, self.s)
            else:
                self.assertNotIn(c, self.s)

    def test_inplace_on_self(self):
        t = self.s.copy()
        t |= t
        self.assertEqual(t, self.s)
        t &= t
        self.assertEqual(t, self.s)
        t -= t
        self.assertEqual(t, self.type2test())
        t = self.s.copy()
        t ^= t
        self.assertEqual(t, self.type2test())

    def test_weakref(self):
        s = self.type2test('gallahad')
        p = weakref.proxy(s)
        self.assertEqual(str(p), str(s))
        s = None
        self.assertRaises(ReferenceError, str, p)

    def test_rich_compare(self):
        class TestRichSetCompare:
            def __gt__(self, some_set):
                self.gt_called = True
                return False

            def __lt__(self, some_set):
                self.lt_called = True
                return False

            def __ge__(self, some_set):
                self.ge_called = True
                return False

            def __le__(self, some_set):
                self.le_called = True
                return False

        # This first tries the builtin rich set comparison, which doesn't know
        # how to handle the custom object. Upon returning NotImplemented, the
        # corresponding comparison on the right object is invoked.
        myset = {1, 2, 3}

        myobj = TestRichSetCompare()
        myset < myobj
        self.assertTrue(myobj.gt_called)

        myobj = TestRichSetCompare()
        myset > myobj
        self.assertTrue(myobj.lt_called)

        myobj = TestRichSetCompare()
        myset <= myobj
        self.assertTrue(myobj.ge_called)

        myobj = TestRichSetCompare()
        myset >= myobj
        self.assertTrue(myobj.le_called)

    @unittest.skipUnless(hasattr(set, "test_c_api"),
                         'C API test only available in a debug build')
    def test_c_api(self):
        self.assertEqual(set().test_c_api(), True)

    def test_equals(self):
        self.assertEqual(self.type2test([]), self.type2test())
        s0_3 = self.type2test([0, 1, 2, 3])
        s0_3_bis = self.type2test(list(s0_3))
        self.assertEqual(s0_3, s0_3_bis)
        self.assertTrue(s0_3 is not s0_3_bis)
        self.assertEqual(s0_3, s0_3)
        self.assertFalse(s0_3 == '0123')
        self.assertTrue(self.type2test([]) != '0123')
        self.assertFalse(s0_3 != s0_3)
        s0_4 = self.type2test([0, 1, 2, 3, 4])
        self.assertNotEqual(s0_3, s0_4)
        s1_4 = self.type2test([1, 2, 3, 4])
        self.assertNotEqual(s0_3, s1_4)

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
        self.assertEqual(len(a1), 2)
        self.assertIn(0, a1)
        self.assertIn(1, a1)
        a1 = self.type2test([0, 1, 2])
        a1.add_all(a1)
        self.assertEqual(len(a1), 3)

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
        with pytest.raises(KeyError):
            a1.remove_all(a2)
