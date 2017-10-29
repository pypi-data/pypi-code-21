#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import unittest
import collections

from . import make_key, LFUDACache, memoize


KEY, VALUE, HITS, PREV, NEXT, THRESHOLD, UPDATES = range(7)


class TestCache(unittest.TestCase):
    @property
    def threshold(self):
        return self.cache._threshold

    @property
    def data(self):
        return self.cache._data

    @property
    def root(self):
        return self.cache._root

    def setUp(self):
        self.size = 5
        self.cache = LFUDACache(self.size)

    def items(self):
        return list(self.cache.items())

    def test_eviction(self):
        items = [(i, 'value for %s' % i) for i in range(self.size + 1)]
        for k, v in items:
            self.cache[k] = v

        self.assertNotIn(0, self.cache)
        self.assertNotIn(0, self.data)

        self.assertListEqual(sorted(self.cache.items()), items[1:])

    def test_pop(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items:
            self.cache[k] = v

        self.assertRaises(KeyError, self.cache.pop, 'wrong-key')

        for k, v in self.items():
            self.cache.get(k, v)  # raise hit counters

        self.cache['another'] = 'value'  # rejected item
        self.assertNotIn('another', self.cache)

        self.assertEqual(self.cache.pop(0), 'value for 0')
        self.assertNotIn(0, self.cache)

        self.cache['another'] = 'value'  # accepted because of cache size
        self.assertEqual(self.cache['another'], 'value')

    def test_clear(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items:
            self.cache[k] = v

        self.cache.clear()
        self.assertListEqual(self.items(), [])

        # Check circularity (empty)
        self.assertIs(self.root, self.root[NEXT])
        self.assertIs(self.root, self.root[NEXT])

        self.cache['a'] = 1
        self.assertListEqual(self.items(), [('a', 1)])

        # Check circularity (1 item)
        self.assertIs(self.root[NEXT], self.root[PREV])
        self.assertIs(self.root, self.root[NEXT][PREV])
        self.assertIs(self.root, self.root[NEXT][NEXT])

    def test_aging(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items:
            self.cache[k] = v

        for k, _ in self.items():
            self.cache.get(k)  # raise hit counter

        self.cache['a1'] = 'va1'  # rejected item
        self.assertNotIn('a1', self.cache)  # do not raise threshold

        self.cache['a2'] = 'va2'  # another rejected item
        self.assertRaises(KeyError, self.cache.__getitem__, 'a2')  # threshold

        self.cache['a3'] = 'va3'  # accepted item
        self.assertEqual(self.cache.get('a3'), 'va3')

        for k, v in self.items():
            self.cache.get(k, v)  # raise hit counter

        self.cache['a4'] = 'v4'  # rejected item
        self.assertNotIn('a4', self.cache)

    def test_ordering(self):
        items = [('a', 0), ('b', 1)]
        for k, v in items:
            self.cache[k] = v

        self.assertListEqual(self.items(), items[::-1])

        self.cache.get('a')

        self.assertListEqual(self.items(), items)

        for k, _ in self.items():
            self.cache.get(k)  # hit

        self.cache['c'] = 2
        items.append(('c', 2))
        self.assertListEqual(self.items(), items)

    def test_drift(self):
        items = [('a', 0), ('b', 1)]
        for k, v in items:
            self.cache[k] = v

        self.cache.get('a')  # hit

        misses = self.root[THRESHOLD]
        self.assertEqual(misses, 0)
        hits = {a[0]: a[2] for a in self.data.values()}
        self.assertEqual(hits['a'], 1)
        self.assertEqual(hits['b'], 0)

        self.cache._drift(1)

        misses = self.root[THRESHOLD]
        self.assertEqual(misses, -1)
        hits = {a[0]: a[2] for a in self.data.values()}
        self.assertEqual(hits['a'], 0)
        self.assertEqual(hits['b'], -1)

    def test_iters(self):
        items = [(i, 'value for %s' % i) for i in range(self.size)]
        for k, v in items[::-1]:
            self.cache[k] = v

        self.assertEqual(list(self.cache), [k for k, _ in items])
        self.assertEqual(list(self.cache.keys()), [k for k, _ in items])
        self.assertEqual(list(self.cache.values()), [v for _, v in items])
        self.assertEqual(list(self.cache.items()), items)

    def test_properties(self):
        self.assertEqual(self.threshold, 0)
        self.cache.get('a')
        self.assertEqual(self.threshold, 1)


class TestMemoize(unittest.TestCase):
    def fnc(self, *args, **kwargs):
        self.calls += 1
        return args, kwargs

    def setUp(self):
        self.calls = 0
        self.memoized = memoize(5)(self.fnc)

    def test_caching(self):
        self.memoized('a')
        self.memoized('a')
        self.assertEqual(self.calls, 1)

        self.calls = 0
        self.memoized('a')
        self.memoized('b')
        self.assertEqual(self.calls, 1)

    def test_expiration(self):
        self.memoized('c')
        self.memoized('d')
        self.memoized('e')
        self.memoized('f')
        self.memoized('g')
        self.memoized('h')
        self.assertEqual(self.calls, 6)

        self.memoized('d')
        self.assertEqual(self.calls, 6)

        self.memoized('c')
        self.assertEqual(self.calls, 7)
