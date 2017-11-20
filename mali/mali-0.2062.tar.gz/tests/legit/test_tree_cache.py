# coding=utf-8
from contextlib import closing

import time

from mali_commands.legit import SqliteConnection
from mali_commands.legit.db_index.cache import SqliteTreeCache
from tests.base import BaseTest


class TestTreeCache(BaseTest):
    db_test_path = ':memory:'

    def create_entry(self):
        ctime = time.time()
        mtime = time.time()
        dev = self.some_random_shit_number_int63()
        ino = self.some_random_shit_number_int63()
        mode = self.some_random_shit_number_int63()
        uid = self.some_random_shit_number_int63()
        gid = self.some_random_shit_number_int63()
        gid = self.some_random_shit_number_int63()
        size = self.some_random_shit_number_int63()
        sha = self.some_random_sha_hash()
        flags = self.some_random_shit_number_int63()

        return ctime, mtime, dev, ino, mode, uid, gid, size, sha, flags

    def _test_scan_folder(self):
        entries = {
            'dogs_cats/dogs/0-99/dog_0.jpg': self.create_entry(),
            'dogs_cats/dogs/0-99/dog_1.jpg': self.create_entry(),
        }

        result = list(SqliteTreeCache._folders_to_scan(entries))
        print(result)

    def _test_simple(self):
        with closing(SqliteConnection({}, path=self.db_test_path)) as connection:
            tree_cache = SqliteTreeCache(connection)

            entries = {
                'dogs_cats/dogs/0-99/dog_0.jpg': self.create_entry(),
                'dogs_cats/dogs/0-99/dog_1.jpg': self.create_entry(),
            }

            tree_cache.set_entries(entries)
