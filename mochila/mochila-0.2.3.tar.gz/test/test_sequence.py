from functools import cmp_to_key
import unittest
import sys

import pytest

import mochila
from test import test_sequence_base
from test import test_mochila

__author__ = 'Horacio Hoyos'
__copyright__ = 'Copyright , Kinori Technologies'


class SequenceTest(test_sequence_base.SequenceTestBase, test_mochila.MochilaTest, unittest.TestCase):

    type2test = mochila.Sequence

    def test_init(self):
        # Iterable arg is optional
        self.assertEqual(self.type2test([]), self.type2test())

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

    def test_constructor_identity(self):
        s = self.type2test(range(3))
        t = self.type2test(s)
        self.assertNotEqual(id(s), id(t))

    def test_repr(self):
        l0 = []
        l2 = [0, 1, 2]
        a0 = self.type2test(l0)
        a2 = self.type2test(l2)

        self.assertEqual(str(a0), str(l0))
        self.assertEqual(repr(a0), repr(l0))
        self.assertEqual(repr(a2), repr(l2))
        self.assertEqual(str(a2), "[0, 1, 2]")
        self.assertEqual(repr(a2), "[0, 1, 2]")

        a2.append(a2)
        a2.append(3)
        self.assertEqual(str(a2), "[0, 1, 2, [...], 3]")
        self.assertEqual(repr(a2), "[0, 1, 2, [...], 3]")

        l0 = []
        for i in range(sys.getrecursionlimit() + 100):
            l0 = [l0]
        self.assertRaises(RuntimeError, repr, l0)

    def test_set_subscript(self):
        a = self.type2test(range(20))
        self.assertRaises(ValueError, a.__setitem__, slice(0, 10, 0), [1, 2, 3])
        self.assertRaises(TypeError, a.__setitem__, slice(0, 10), 1)
        self.assertRaises(ValueError, a.__setitem__, slice(0, 10, 2), [1, 2])
        self.assertRaises(TypeError, a.__getitem__, 'x', 1)
        a[slice(2, 10, 3)] = [1, 2, 3]
        self.assertEqual(a, self.type2test([0, 1, 1, 3, 4, 2, 6, 7, 3,
                                            9, 10, 11, 12, 13, 14, 15,
                                            16, 17, 18, 19]))

    def test_setitem(self):
        a = self.type2test([0, 1])
        a[0] = 0
        a[1] = 100
        self.assertEqual(a, self.type2test([0, 100]))
        a[-1] = 200
        self.assertEqual(a, self.type2test([0, 200]))
        a[-2] = 100
        self.assertEqual(a, self.type2test([100, 200]))
        self.assertRaises(IndexError, a.__setitem__, -3, 200)
        self.assertRaises(IndexError, a.__setitem__, 2, 200)

        a = self.type2test([])
        self.assertRaises(IndexError, a.__setitem__, 0, 200)
        self.assertRaises(IndexError, a.__setitem__, -1, 200)
        self.assertRaises(TypeError, a.__setitem__)

        a = self.type2test([0, 1, 2, 3, 4])
        a[0] = 1
        a[1] = 2
        a[2] = 3
        self.assertEqual(a, self.type2test([1, 2, 3, 3, 4]))
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

    def test_setslice(self):
        l = [0, 1]
        a = self.type2test(l)

        for i in range(-3, 4):
            a[:i] = l[:i]
            self.assertEqual(a, self.type2test(l))
            a2 = a[:]
            a2[:i] = a[:i]
            self.assertEqual(self.type2test(a2), a)
            a[i:] = l[i:]
            self.assertEqual(a, self.type2test(l))
            a2 = a[:]
            a2[i:] = a[i:]
            self.assertEqual(self.type2test(a2), a)
            for j in range(-3, 4):
                a[i:j] = l[i:j]
                self.assertEqual(a, self.type2test(l))
                a2 = a[:]
                a2[i:j] = a[i:j]
                self.assertEqual(self.type2test(a2), a)

        aa2 = a2[:]
        aa2[:0] = [-2, -1]
        self.assertEqual(aa2, self.type2test([-2, -1, 0, 1]))
        aa2[0:] = []
        self.assertEqual(aa2, self.type2test([]))

        a = self.type2test([1, 2, 3, 4, 5])
        a[:-1] = a
        self.assertEqual(a, self.type2test([1, 2, 3, 4, 5, 5]))
        a = self.type2test([1, 2, 3, 4, 5])
        a[1:] = a
        self.assertEqual(a, self.type2test([1, 1, 2, 3, 4, 5]))
        a = self.type2test([1, 2, 3, 4, 5])
        a[1:-1] = a
        self.assertEqual(a, self.type2test([1, 1, 2, 3, 4, 5, 5]))

        a = self.type2test([])
        a[:] = tuple(range(10))
        self.assertEqual(a, self.type2test(range(10)))

        self.assertRaises(TypeError, a.__setitem__, slice(0, 1, 5))

        self.assertRaises(TypeError, a.__setitem__)

    def test_delslice(self):
        a = self.type2test([0, 1])
        del a[1:2]
        del a[0:1]
        self.assertEqual(a, self.type2test([]))

        a = self.type2test([0, 1])
        del a[1:2]
        del a[0:1]
        self.assertEqual(a, self.type2test([]))

        a = self.type2test([0, 1])
        del a[-2:-1]
        self.assertEqual(a, self.type2test([1]))

        a = self.type2test([0, 1])
        del a[-2:-1]
        self.assertEqual(a, self.type2test([1]))

        a = self.type2test([0, 1])
        del a[1:]
        del a[:1]
        self.assertEqual(a, self.type2test([]))

        a = self.type2test([0, 1])
        del a[1:]
        del a[:1]
        self.assertEqual(a, self.type2test([]))

        a = self.type2test([0, 1])
        del a[-1:]
        self.assertEqual(a, self.type2test([0]))

        a = self.type2test([0, 1])
        del a[-1:]
        self.assertEqual(a, self.type2test([0]))

        a = self.type2test([0, 1])
        del a[:]
        self.assertEqual(a, self.type2test([]))

    def test_append(self):
        a = self.type2test([])
        a.append(0)
        a.append(1)
        a.append(2)
        self.assertEqual(a, self.type2test([0, 1, 2]))

        self.assertRaises(TypeError, a.append)

    def test_extend(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a = a1[:]
        a.extend(a2)
        self.assertEqual(len(a), len(a1) + len(a2))
        self.assertTrue(0 in a)
        self.assertTrue(1 in a)

        a.extend(self.type2test([]))
        self.assertEqual(len(a), len(a1) + len(a2))
        a.extend(a)
        self.assertEqual(a, self.type2test([0, 0, 1, 0, 0, 1]))

        a = self.type2test("spam")
        a.extend("eggs")
        self.assertEqual(a, self.type2test("spameggs"))

        self.assertRaises(TypeError, a.extend, None)

        self.assertRaises(TypeError, a.extend)

    def test_insert(self):
        a = self.type2test([0, 1, 2])
        a.insert(0, -2)
        a.insert(1, -1)
        a.insert(2, 0)
        self.assertEqual(a, self.type2test([-2, -1, 0, 0, 1, 2]))

        b = a[:]
        b.insert(-2, "foo")
        b.insert(-200, "left")
        b.insert(200, "right")
        self.assertEqual(b, self.type2test(["left", -2, -1, 0, 0, "foo", 1, 2, "right"]))
        self.assertRaises(TypeError, a.insert)

    def test_pop(self):
        a = self.type2test([-1, 0, 1])
        a.pop()
        self.assertEqual(a, self.type2test([-1, 0]))
        a.pop(0)
        self.assertEqual(a, self.type2test([0]))
        self.assertRaises(IndexError, a.pop, 5)
        a.pop(0)
        self.assertEqual(a, self.type2test())
        self.assertRaises(IndexError, a.pop)
        self.assertRaises(TypeError, a.pop, 42, 42)

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
        e = self.type2test(d)
        self.assertRaises(BadExc, d.remove, 'c')
        for x, y in zip(d, e):
            # verify that original order and values are retained.
            self.assertIs(x, y)

    def test_index(self):
        super().test_index()
        a = self.type2test([-2, -1, 0, 0, 1, 2])
        a.remove(0)
        self.assertRaises(ValueError, a.index, 2, 0, 4)
        self.assertEqual(a, self.type2test([-2, -1, 0, 1, 2]))

        # Test modifying the list during index's iteration
        class EvilCmp:
            def __init__(self, victim):
                self.victim = victim

            def __eq__(self, other):
                del self.victim[:]
                return False

        a = self.type2test()
        a[:] = [EvilCmp(a) for _ in range(100)]
        # This used to seg fault before patch #1005778
        self.assertRaises(ValueError, a.index, None)

    def test_reverse(self):
        u = self.type2test([-2, -1, 0, 1, 2])
        u2 = u[:]
        u.reverse()
        self.assertEqual(u, self.type2test([2, 1, 0, -1, -2]))
        u.reverse()
        self.assertEqual(u, self.type2test(u2))
        self.assertRaises(TypeError, u.reverse, 42)

    def test_clear(self):
        u = self.type2test([2, 3, 4])
        u.clear()
        self.assertEqual(len(u), 0)

        u = self.type2test([])
        u.clear()
        self.assertEqual(len(u), 0)

        u = self.type2test([])
        u.append(1)
        u.clear()
        u.append(2)
        self.assertEqual(len(u), 1)

        self.assertRaises(TypeError, u.clear, None)

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
        v.append('i')
        self.assertTrue('a' in v)
        self.assertTrue('b' in v)
        self.assertTrue('i' in v)
        self.assertFalse('i' in u)

        # test that it's a shallow, not a deep copy
        u = self.type2test([1, 2, [3, 4], 5])
        v = u.copy()
        self.assertEqual(u, v)
        self.assertIs(v[2], u[2])

        self.assertRaises(TypeError, u.copy, None)

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
            z.append(1)
            if x == y:
                return 0
            elif x < y:
                return -1
            else:  # x > y
                return 1

        self.assertRaises(ValueError, z.sort,
                          key=cmp_to_key(selfmodifyingComparison))

        self.assertRaises(TypeError, z.sort, 42, 42, 42, 42)

    def test_slice(self):
        u = self.type2test("spam")
        u[:2] = "h"
        self.assertEqual(u, self.type2test(list("ham")))

    def test_get_iterable(self):
        u = self.type2test("spam")
        indices = [1, 3, 0]
        items = u[indices]
        self.assertListEqual(items._items, ['p', 'm', 's'])

    def test_iadd(self):
        super().test_iadd()
        u = self.type2test([0, 1])
        u2 = u
        u += [2, 3]
        self.assertIs(u, u2)

        u = self.type2test("spam")
        u += "eggs"
        self.assertEqual(u, self.type2test("spameggs"))

        self.assertRaises(TypeError, u.__iadd__, None)

    def test_imul(self):
        u = self.type2test([0, 1])
        with pytest.raises(TypeError):
            u *= 3

    def test_extendedslicing(self):
        #  subscript
        a = self.type2test([0, 1, 2, 3, 4])

        #  deletion
        del a[::2]
        self.assertEqual(a, self.type2test([1, 3]))
        a = self.type2test(range(5))
        del a[1::2]
        self.assertEqual(a, self.type2test([0, 2, 4]))
        a = self.type2test(range(5))
        del a[1::-2]
        self.assertEqual(a, self.type2test([0, 2, 3, 4]))
        a = self.type2test(range(10))
        del a[::1000]
        self.assertEqual(a, self.type2test([1, 2, 3, 4, 5, 6, 7, 8, 9]))
        #  assignment
        a = self.type2test(range(10))
        a[::2] = [-1] * 5
        self.assertEqual(a, self.type2test([-1, 1, -1, 3, -1, 5, -1, 7, -1, 9]))
        a = self.type2test(range(10))
        a[::-4] = [10] * 3
        self.assertEqual(a, self.type2test([0, 10, 2, 3, 4, 10, 6, 7, 8, 10]))
        a = self.type2test(range(4))
        a[::-1] = a
        self.assertEqual(a, self.type2test([3, 2, 1, 0]))
        a = self.type2test(range(10))
        b = a[:]
        c = a[:]
        a[2:3] = self.type2test(["two", "elements"])
        b[slice(2, 3)] = self.type2test(["two", "elements"])
        c[2:3:] = self.type2test(["two", "elements"])
        self.assertEqual(a, self.type2test(b))
        self.assertEqual(a, self.type2test(c))
        a = self.type2test(range(10))
        a[::2] = tuple(range(5))
        self.assertEqual(a, self.type2test([0, 1, 1, 3, 2, 5, 3, 7, 4, 9]))
        # test issue7788
        a = self.type2test(range(10))
        del a[9::1 << 333]

    def test_constructor_exception_handling(self):
        # Bug #1242657
        class F(object):
            def __iter__(self):
                raise KeyboardInterrupt

        self.assertRaises(KeyboardInterrupt, list, F())

    def test_truth(self):
        self.assertTrue(not self.type2test([]))
        self.assertTrue(self.type2test([42]))

    def test_identity(self):
        self.assertTrue([] is not [])

    def test_len(self):
        super().test_len()
        self.assertEqual(len([]), 0)
        self.assertEqual(len([0]), 1)
        self.assertEqual(len([0, 1, 2]), 3)

    def test_overflow(self):
        lst = [4, 5, 6, 7]
        n = int((sys.maxsize * 2 + 2) // len(lst))

        def mul(a, b): return a * b

        def imul(a, b): a *= b

        self.assertRaises((MemoryError, OverflowError), mul, lst, n)
        self.assertRaises((MemoryError, OverflowError), imul, lst, n)

    def test_repr_large(self):
        # Check the repr of large list objects
        def check(n):
            l = [0] * n
            s = repr(l)
            self.assertEqual(s,
                             '[' + ', '.join(['0'] * n) + ']')

        check(10)  # check our checking code
        check(1000000)

    def test_equals(self):
        self.assertEqual(self.type2test([]), self.type2test())
        l0_3 = self.type2test([0, 1, 2, 3])
        l0_3_bis = self.type2test(list(l0_3))
        self.assertEqual(l0_3, l0_3_bis)
        self.assertTrue(l0_3 is not l0_3_bis)
        self.assertEqual(l0_3, l0_3)
        self.assertFalse(l0_3 == '0123')
        self.assertTrue(self.type2test([]) != '0123')
        self.assertFalse(l0_3 != l0_3)
        l0_4 = self.type2test([0, 1, 2, 3, 4])
        self.assertNotEqual(l0_3, l0_4)
        l1_4 = self.type2test([1, 2, 3, 4])
        self.assertNotEqual(l0_3, l1_4)

    def test_sort_by_reverse(self):
        def by_rank(agent):
            return agent.rank

        mochila = self.type2test(test_mochila.agents.values())
        ordered_ranks = ["539-35-1184", "730-46-0957", "424-16-0664", "861-26-2185", "212-70-6483", "368-95-4835",
                         "694-68-6118", "859-05-6244", "824-34-4142", "186-01-5810", ]
        sorted = mochila.sort_by(by_rank, reverse=True)
        for i, code in enumerate(reversed(ordered_ranks)):
            agent = test_mochila.agents[code]
            self.assertEqual(agent, sorted[i])

    def test_sort_by_inplace(self):
        def by_rank(agent):
            return agent.rank

        mochila = self.type2test(test_mochila.agents.values())
        ordered_ranks = ["539-35-1184", "730-46-0957", "424-16-0664", "861-26-2185", "212-70-6483", "368-95-4835",
                         "694-68-6118", "859-05-6244", "824-34-4142", "186-01-5810", ]
        mochila.sort_by(by_rank, inplace=True)
        for i, code in enumerate(ordered_ranks):
            agent = test_mochila.agents[code]
            self.assertEqual(agent, mochila[i])

    def test_add_all(self):
        a1 = self.type2test([0])
        a2 = self.type2test((0, 1))
        a = a1[:]
        a.add_all(a2)
        self.assertEqual(len(a), len(a1) + len(a2))
        self.assertIn(0, a)
        self.assertIn(1, a)
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


