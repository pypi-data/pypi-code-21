#!/usr/bin/env python


"""Tests for `DictCache."""


import unittest

from smartbotsol import DictCache, User



class TestSmartbotsol(unittest.TestCase):
    """Tests for `smartbotsol` package."""

    def setUp(self):
        """Set up test fixtures, if any."""
        self.dump_path = './backups'
        # self.test_user = 123456
        self.users_uids = [ 111,222,333 ]
        self.dict_cache = { x: User(x) for x in self.users_uids }
        import dill
        self.dump = dill.dumps(self.dict_cache)

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_user(self):
        """Test something."""
        cache = DictCache()
        for u in self.users_uids:
            cache.get(u)
        for u in self.users_uids:
            self.assertEqual(cache.get(u), User(u))

    def test_to_dict(self):
        """Test something."""
        cache = DictCache(self.dict_cache)
        # self.assertTrue(isinstance(cache.to_dict(), dict))
        self.assertDictEqual(cache.to_dict(), self.dict_cache)


    def test_from_dict(self):
        cache = DictCache.from_dict(self.dict_cache)
        self.assertTrue(isinstance(cache._cache, dict))
        self.assertDictEqual(cache._cache, self.dict_cache)
