# -*- coding: utf-8 -*-

import os
import time
import unittest
from cachingutil.file_cache import FileCache
from cachingutil.memory_cache import SimpleMemoryCache


class IntervalMemoryCache(SimpleMemoryCache):
    """
    simple cache for times. the time for each key
    will stay the same for the interval given by
    max_age on instantiation
    """
    def key(self,
            key):
        return key

    def fetch_from_source(self,
                          key):
        return time.time()


class TestMemoryCaching(unittest.TestCase):

    def setUp(self):
        # Set up an Iterval cache with values
        # expiring after 5s
        self.cache = IntervalMemoryCache(max_age = 3)

    def tearDown(self):
        pass

    def test_fetch(self):
        """
        runs over 1 seconds iterations over 10 seconds
        with two items in the cache, 'a' and 'b'. The cache
        max_age is 3s

        ┌───────────┬──────────┬──────────┐
        │ Iteration │ source a │ source b │
        ├───────────┼──────────┼──────────┤
        │      1    │  source  │     -    │
        │      2    │   cache  │  source  │
        │      3    │   cache  │   cache  │
        │      4    │  source  │   cache  │
        │      5    │   cache  │  source  │
        │      6    │   cache  │   cache  │
        │      7    │  source  │   cache  │
        │      8    │   cache  │  source  │
        │      9    │   cache  │   cache  │
        │     10    │  source  │   cache  │
        └───────────┴──────────┴──────────┘


        """
        fetched_a = self.cache.fetch(key = u'a')
        a_from_cache = None

        fetched_b = None
        b_from_cache = None

        for i in range(10):

            ia = i
            ib = i - 1  # b is one iteration behind a

            print u'a', ia, fetched_a, a_from_cache
            print u'b', ib, fetched_b, b_from_cache

            expect_a_from_source = ia % 3 == 0  # new set of 3 for a ?
            if expect_a_from_source:
                # first fetch or cache item expired, fetch is from source
                self.assertNotEqual(fetched_a, a_from_cache)
            else:
                # item in caceh and not expired. Item is from caceh.
                self.assertEqual(fetched_a, a_from_cache)

            if ib > -1:  # do nothing on the first iteration for b
                expect_b_from_source = ib % 3 == 0
                if expect_b_from_source:
                    # first fetch or cache item expired, fetch is from source
                    self.assertNotEqual(fetched_b, b_from_cache)
                else:
                    # first fetch or cache item expired, fetch is from source
                    self.assertEqual(fetched_b, b_from_cache)

            time.sleep(1)

            a_from_cache = self.cache.fetch(key = u'a')
            if expect_a_from_source:
                # next iteration, we expect these to match
                fetched_a = a_from_cache

            if ib > -1:  # Don't do this until b is active
                b_from_cache = self.cache.fetch(key = u'b')

                if expect_b_from_source and ib > 0:
                    # next iteration, we expect these to match
                    fetched_b = b_from_cache
            else:
                # prepare for first iteration for b
                fetched_b = self.cache.fetch(key = u'b')


class IntervalFileCache(FileCache):
    """
    simple cache for times. the time for each key
    will stay the same for the interval given by
    max_age on instantiation
    """

    def filename(self,
                 filename):
        return u'{filename}.cache'.format(filename = filename)

    def fetch_from_source(self,
                          filename):
        return int(time.time())

    @staticmethod
    def encode(data):
        return int(data)

    @staticmethod
    def decode(encoded):
        return int(encoded)


class TestFileCaching(unittest.TestCase):

    FOLDER = u'.{s}test_data{s}test_caching'.format(s=os.sep)
    MAX_AGE = 3

    def setUp(self):
        # Set up an Interval cache with values
        # expiring after 5s
        self.cache = IntervalFileCache(max_age = self.MAX_AGE,
                                       folder  = self.FOLDER)

    def tearDown(self):
        for filename in (u'a',  u'b'):
            try:
                os.remove(self.cache.key(filename = filename))
            except Exception:
                pass
        try:
            os.rmdir(self.FOLDER)
        except Exception:
            pass

    def test_key(self):

        data = {u'abc'     : u'abc.cache',
                u'temp/abc': u'temp/abc.cache'}
        for filename, path in iter(data.items()):
            self.assertEqual(self.cache.key(filename = filename),
                             os.path.normpath(os.path.join(self.FOLDER, path)))

    def test_fetch(self):
        """
        runs over 1 seconds iterations over 10 seconds
        with two items in the cache, 'a' and 'b'. The cache
        max_age is 3s

        ┌───────────┬──────────┬──────────┐
        │ Iteration │ source a │ source b │
        ├───────────┼──────────┼──────────┤
        │      1    │  source  │     -    │
        │      2    │   cache  │  source  │
        │      3    │   cache  │   cache  │
        │      4    │  source  │   cache  │
        │      5    │   cache  │  source  │
        │      6    │   cache  │   cache  │
        │      7    │  source  │   cache  │
        │      8    │   cache  │  source  │
        │      9    │   cache  │   cache  │
        │     10    │  source  │   cache  │
        └───────────┴──────────┴──────────┘


        """
        fetched_a = self.cache.fetch(filename = u'a')
        a_from_cache = None

        fetched_b = None
        b_from_cache = None

        for i in range(10):

            ia = i
            ib = i - 1  # b is one iteration behind a

            expect_a_from_source = ia % self.MAX_AGE == 0  # new set of 3 for a ?
            if expect_a_from_source:
                # first fetch or cache item expired, fetch is from source
                self.assertNotEqual(fetched_a, a_from_cache)
            else:
                # item in caceh and not expired. Item is from caceh.
                self.assertEqual(fetched_a, a_from_cache)

            if ib > -1:  # do nothing on the first iteration for b
                expect_b_from_source = ib % self.MAX_AGE == 0
                if expect_b_from_source:
                    # first fetch or cache item expired, fetch is from source
                    self.assertNotEqual(fetched_b, b_from_cache)
                else:
                    # first fetch or cache item expired, fetch is from source
                    self.assertEqual(fetched_b, b_from_cache)

            time.sleep(1)

            a_from_cache = self.cache.fetch(filename = u'a')
            if expect_a_from_source:
                # next iteration, we expect these to match
                fetched_a = a_from_cache

            if ib > -1:  # Don't do this until b is active
                b_from_cache = self.cache.fetch(filename = u'b')

                if expect_b_from_source and ib > 0:
                    # next iteration, we expect these to match
                    fetched_b = b_from_cache
            else:
                # prepare for first iteration for b
                fetched_b = self.cache.fetch(filename = u'b')


if __name__ == u'__main__':
    unittest.main()
