from functools import cmp_to_key
import unittest
import weakref
import sys

import mochila
from test import test_set_base, test_sequence_base
from test import test_mochila

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class OrderedSetTest(test_sequence_base.SequenceTestBase, test_mochila.MochilaTest, test_set_base.SetTestBase, unittest.TestCase):

    type2test = mochila.OrderedSet
    basetype = mochila.OrderedSet

    def test_init(self):
        # Set like init
        s = self.type2test()
        s.__init__(self.word)
        w = []
        for c in self.word:
            if c not in w:
                w.append(c)
        self.assertEqual(s._items, w)
        s.__init__(self.otherword)
        w = []
        for c in self.otherword:
            if c not in w:
                w.append(c)
        self.assertEqual(s._items, w)

        l = self.type2test()
        self.assertRaises(TypeError, l.__init__, (), 2)
        self.assertRaises(TypeError, l.__init__, (), a=12)

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

    def test_pop_sequence(self):
        a = self.type2test([-1, 0, 1])
        # Remove random item
        elem = a.pop()
        self.assertFalse(elem in a)
        # Remove from index
        first = a[0]
        elem = a.pop(0)
        self.assertEquals(first, elem)
        self.assertEqual(1, len(a))
        self.assertRaises(IndexError, a.pop, 5)
        a.pop(0)
        self.assertEqual(a, self.type2test())
        self.assertRaises(KeyError, a.pop)
        self.assertRaises(TypeError, a.pop, 42, 42)

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

    def test_and(self):
        # and picks form the other first
        intr = [l for l in self.otherword if l in self.word]
        i = self.type2test(intr)
        self.assertEqual(self.s & self.type2test(self.otherword), i)
        self.assertEqual(self.s & self.otherword, i)

    def test_or(self):
        i = self.type2test([e for s in (self.word, self.otherword) for e in s])
        self.assertEqual(self.s | self.type2test(self.otherword), i)
        self.assertEqual(self.s | self.otherword, i)

    def test_sub(self):
        i = self.type2test([e for e in self.word if e not in self.otherword])
        self.assertEqual(self.s - self.type2test(self.otherword), i)
        self.assertEqual(self.s - self.otherword, i)

    def test_xor(self):
        all = [e for e in self.word if e not in self.otherword]
        all.extend([e for e in self.otherword if e not in self.word])
        i = self.type2test(all)
        self.assertEqual(self.s ^ self.type2test(self.otherword), i)
        self.assertEqual(self.s ^ self.otherword, i)

    def test_contains_fake(self):
        # Set elements need to be hashable
        class AllEq:
            # Sequences must use rich comparison against each item
            # (unless "is" is true, or an earlier item answered)
            # So instances of AllEq must be found in all non-empty sequences.
            def __eq__(self, other):
                return True

            __hash__ = None  # Can't meet hash invariant requirements
        with self.assertRaises(TypeError):
            AllEq() not in self.type2test([])
            AllEq() in self.type2test([1])


    def test_contains_order(self):
        # sets test containment by key
        pass

    def test_count(self):
        # No counting on sets
        pass

    def test_getslice(self):
        l = [0, 1, 2, 3, 4]
        u = self.type2test(l)
        self.assertEqual(u[0:0], self.type2test([]))
        self.assertEqual(u[1:2], self.type2test([1]))
        self.assertEqual(u[-2:-1], self.type2test([3]))
        self.assertEqual(u[-1000:1000], self.type2test([0, 1, 2, 3, 4]))
        self.assertEqual(u[1000:-1000], self.type2test([]))
        self.assertEqual(u[:], self.type2test([0, 1, 2, 3, 4]))
        self.assertEqual(u[1:None], self.type2test([1, 2, 3, 4]))
        self.assertEqual(u[None:3], self.type2test([0, 1, 2]))

        # Extended slices
        self.assertEqual(u[::], u)
        self.assertEqual(u[::2], self.type2test([0, 2, 4]))
        self.assertEqual(u[1::2], self.type2test([1, 3]))
        self.assertEqual(u[::-1], self.type2test([4, 3, 2, 1, 0]))
        self.assertEqual(u[::-2], self.type2test([4, 2, 0]))
        self.assertEqual(u[3::-2], self.type2test([3, 1]))
        self.assertEqual(u[3:3:-2], self.type2test([]))
        self.assertEqual(u[3:2:-2], self.type2test([3]))
        self.assertEqual(u[3:1:-2], self.type2test([3]))
        self.assertEqual(u[3:0:-2], self.type2test([3, 1]))
        self.assertEqual(u[::-100], self.type2test([4]))
        self.assertEqual(u[100:-100:], self.type2test([]))
        self.assertEqual(u[-100:100:], self.type2test([0, 1, 2, 3, 4]))
        self.assertEqual(u[100:-100:-1], u[::-1])
        self.assertEqual(u[-100:100:-1], self.type2test([]))
        self.assertEqual(u[-100:100:2], self.type2test([0, 2, 4]))

        # Test extreme cases with long ints
        a = self.type2test([0, 1, 2, 3, 4])
        self.assertEqual(a[-pow(2, 128): 3], self.type2test([0, 1, 2]))
        self.assertEqual(a[3: pow(2, 145)], self.type2test([3, 4]))

        # Slice [:] is a copy
        u = self.type2test(l)
        a = u[:]
        a.append(5)
        self.assertFalse(5 in u)

    def test_subscript(self):
        a = self.type2test([10, 11])
        self.assertEqual(a.__getitem__(0), 10)
        self.assertEqual(a.__getitem__(1), 11)
        self.assertEqual(a.__getitem__(-2), 10)
        self.assertEqual(a.__getitem__(-1), 11)
        self.assertRaises(IndexError, a.__getitem__, -3)
        self.assertRaises(IndexError, a.__getitem__, 3)
        self.assertEqual(a.__getitem__(slice(0, 1)), self.type2test([10]))
        self.assertEqual(a.__getitem__(slice(1, 2)), self.type2test([11]))
        self.assertEqual(a.__getitem__(slice(0, 2)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(0, 3)), self.type2test([10, 11]))
        self.assertEqual(a.__getitem__(slice(3, 5)), self.type2test([]))
        self.assertRaises(ValueError, a.__getitem__, slice(0, 10, 0))
        self.assertRaises(TypeError, a.__getitem__, 'x')

    def test_iadd(self):
        # No iadd for sets
        pass

    def test_index(self):
        u = self.type2test([0, 1])
        self.assertEqual(u.index(0), 0)
        self.assertEqual(u.index(1), 1)
        self.assertRaises(ValueError, u.index, 2)

        u = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(u.index(0), 2)
        self.assertEqual(u.index(0, 2), 2)
        self.assertEqual(u.index(-2, -10), 0)
        self.assertEqual(u.index(2, 0, -10), 4)

        self.assertRaises(TypeError, u.index)

        a = self.type2test([-2, -1, 0, 0, 1, 2])
        self.assertEqual(a.index(0, -4), 2)
        self.assertEqual(a.index(-2, -10), 0)
        self.assertEqual(a.index(0, 2, 4), 2)
        self.assertEqual(a.index(0, -3, -2), 2)
        self.assertEqual(a.index(0, -4 * sys.maxsize, 4 * sys.maxsize), 2)

        a = self.type2test([-2, -1, 0, 1, 2])
        index = a.index([-2, -1])
        self.assertEqual(index, [0, 1])
        index = a.index([1, 0, -2])
        self.assertEqual(index, [3, 2, 0])


    def test_getitem_iterator(self):
        u = self.type2test(['a', 'b', 'c', 'd', 'e'])
        items = [0, 1]
        self.assertEqual(u[items], self.type2test(['a', 'b']))
        items = [2, 4, 0]
        self.assertEqual(u[items], self.type2test(['c', 'e', 'a']))

    def test_setitem(self):
        a = self.type2test([0, 1])
        a[0] = 0
        a[1] = 100
        self.assertEqual(a, self.type2test([0, 100]))
        a[-1] = 200
        self.assertEqual(a, self.type2test([0, 200]))
        a[-2] = 100
        self.assertEqual(a, self.type2test([100, 200]))
        self.assertRaises(IndexError, a.__setitem__, -3, 300)
        self.assertRaises(IndexError, a.__setitem__, 2, 300)

        a = self.type2test([])
        self.assertRaises(IndexError, a.__setitem__, 0, 200)
        self.assertRaises(IndexError, a.__setitem__, -1, 200)
        self.assertRaises(TypeError, a.__setitem__)

        a = self.type2test([0, 1, 2, 3, 4])
        a[0] = 1
        self.assertEqual(a, self.type2test([0, 1, 2, 3, 4]))
        a[2] = 3
        self.assertEqual(a, self.type2test([0, 1, 2, 3, 4]))
        a[0] = 5
        a[1] = 6
        a[2] = 7
        self.assertEqual(a, self.type2test([5, 6, 7, 3, 4]))
        a[-2] = 88
        a[-1] = 99
        self.assertEqual(a, self.type2test([5, 6, 7, 88, 99]))
        a[-2] = 8
        a[-1] = 9
        self.assertEqual(a, self.type2test([5, 6, 7, 8, 9]))

    def test_insert(self):
        a = self.type2test(['a', 'b', 'c'])
        a.insert(0, 'C')
        a.insert(1, 'B')
        a.insert(2, 'A')
        self.assertEqual(a, self.type2test(['C', 'B', 'A', 'a', 'b', 'c']))

        b = a[:]
        b.insert(-2, "foo")
        b.insert(-200, "left")
        b.insert(200, "right")
        self.assertEqual(b, self.type2test(["left", 'C', 'B', 'A', 'a', "foo", 'b', 'c', "right"]))
        self.assertRaises(TypeError, a.insert)

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

    def test_sort(self):
        u = self.type2test([1, 0])
        u.sort()
        self.assertEqual(u, self.type2test([0, 1]))

        u = self.type2test([2, 1, 0, -1, -2])
        u.sort()
        self.assertEqual(u, self.type2test([-2, -1, 0, 1, 2]))

        self.assertRaises(TypeError, u.sort, 42, 42)

        def revcmp(a, b):
            if a == b:
                return 0
            elif a < b:
                return 1
            else:  # a > b
                return -1

        u.sort(key=cmp_to_key(revcmp))
        self.assertEqual(u, self.type2test([2, 1, 0, -1, -2]))

        # The following dumps core in unpatched Python 1.5:
        def myComparison(x, y):
            xmod, ymod = x % 3, y % 7
            if xmod == ymod:
                return 0
            elif xmod < ymod:
                return -1
            else:  # xmod > ymod
                return 1

        z = self.type2test(range(12))
        z.sort(key=cmp_to_key(myComparison))

        self.assertRaises(TypeError, z.sort, 2)

        def selfmodifyingComparison(x, y):
            z.append(12)
            if x == y:
                return 0
            elif x < y:
                return -1
            else:  # x > y
                return 1

        self.assertRaises(ValueError, z.sort,
                          key=cmp_to_key(selfmodifyingComparison))

        self.assertRaises(TypeError, z.sort, 42, 42, 42, 42)
