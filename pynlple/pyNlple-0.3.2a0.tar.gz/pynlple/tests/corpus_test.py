# -*- coding: utf-8 -*-
import unittest
from pynlple.data.corpus import StackingSource, DeduplicatingFixedCacheSizeSource


class StackingSourceTest(unittest.TestCase):

    def setUp(self):
        self.source1 = [
            '1', '2', '3'
        ]
        self.source2 = [
            4, 5, 6
        ]

    def test_should_return_all_items_consequently(self):
        stacking_source = StackingSource([self.source1, self.source2])
        expected_items = ['1', '2', '3', 4, 5, 6]

        self.assertEqual(expected_items, [item for item in stacking_source])


class DeduplicatingFixedCacheSizeSourceTest(unittest.TestCase):

    def setUp(self):
        self.source = [1, 1, 2, 2, 3, 1, 2, 4, 5, 1, 1, 2, 2, 3, 3, 4, 6, 7]

    def test_should_yield_deduplicated_no_cache_overflow(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=15)

        expected_result = [1, 2, 3, 4, 5, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_partially_deduplicated_cache_overflow(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=4, refresh=False)

        expected_result = [1, 2, 3, 4, 5, 1, 2, 3, 4, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])

    def test_should_yield_partially_deduplicated_cache_overflow_refreshing(self):
        dedup_source = DeduplicatingFixedCacheSizeSource(self.source, cache_size=4, refresh=True)

        expected_result = [1, 2, 3, 4, 5, 3, 4, 6, 7]
        self.assertEqual(expected_result, [i for i in dedup_source])