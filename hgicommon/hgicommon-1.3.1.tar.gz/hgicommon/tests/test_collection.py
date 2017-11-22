"""
Legalese
--------
Copyright (c) 2016 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import copy
import unittest
from collections import defaultdict
from threading import Semaphore
from threading import Thread
from time import sleep

from hgicommon.collections import Metadata, ThreadSafeDefaultdict


class TestThreadSafeDefaultdict(unittest.TestCase):
    """
    Tests for `ThreadSafeDefaultdict`.
    """
    def test_is_defaultdict(self):
        self.assertIsInstance(ThreadSafeDefaultdict(), defaultdict)

    def test_getitem_can_be_used_to_get_valeus(self):
        thread_safe_dict = ThreadSafeDefaultdict(object)
        item_at_zero = thread_safe_dict[0]
        self.assertEqual(thread_safe_dict[1], thread_safe_dict[1])
        self.assertNotEqual(thread_safe_dict[2], thread_safe_dict[3])
        self.assertEqual(item_at_zero, thread_safe_dict[0])

    def test_getitem_is_threadsafe(self):
        # `defaultdict` will fail this test!
        number_of_threads = 100
        values = []

        def object_factory() -> object:
            # This sleep triggers a context switch if there are other threads running
            sleep(0.1)
            created = object()
            values.append(created)
            return created

        thread_safe_dict = ThreadSafeDefaultdict(object_factory)
        values_of_foo = []
        wait_semaphore = Semaphore(0)

        def get_and_store_foo_value():
            values_of_foo.append(thread_safe_dict["foo"])
            wait_semaphore.release()

        for _ in range(number_of_threads):
            Thread(target=get_and_store_foo_value).start()

        for _ in range(number_of_threads):
            wait_semaphore.acquire()

        assert len(values_of_foo) == number_of_threads
        for i in range(number_of_threads - 1):
            self.assertEqual(values_of_foo[i], values_of_foo[i + 1])


class TestMetadata(unittest.TestCase):
    """
    Tests for `Metadata`.
    """
    _TEST_VALUES = {1: 2, 3: 4}

    def setUp(self):
        self.metadata = Metadata(TestMetadata._TEST_VALUES)

    def test_init_with_no_values(self):
        self.assertEqual(len(Metadata()), 0)

    def test_init_with_values(self):
        self.assertCountEqual(self.metadata.keys(), TestMetadata._TEST_VALUES.keys())
        self.assertCountEqual(self.metadata.values(), TestMetadata._TEST_VALUES.values())

    def test_get(self):
        self.assertEqual(self.metadata.get(1), TestMetadata._TEST_VALUES[1])
        self.assertEqual(self.metadata[1], TestMetadata._TEST_VALUES[1])

    def test_rename(self):
        self.metadata.rename(1, 10)
        self.assertNotIn(1, self.metadata)
        self.assertEqual(self.metadata[10], 2)

    def test_rename_non_existent(self):
        self.assertRaises(KeyError, self.metadata.rename, 10, 20)

    def test_rename_to_same_name(self):
        self.metadata.rename(1, 1)
        self.assertEqual(self.metadata[1], 2)

    def test_pop(self):
        self.metadata.pop(1)
        self.assertEqual(self.metadata, Metadata({3: 4}))

    def test_clear(self):
        self.metadata.clear()
        self.assertEqual(self.metadata, Metadata())

    def test_delete(self):
        del self.metadata[1]
        self.assertEqual(self.metadata, Metadata({3: 4}))

    def test_len(self):
        self.assertEqual(len(self.metadata), 2)

    def test_items(self):
        self.assertCountEqual(self.metadata.items(), [(1, 2), (3, 4)])

    def test_values(self):
        self.assertCountEqual(self.metadata.values(), [2, 4])

    def test_keys(self):
        self.assertCountEqual(self.metadata.keys(), [1, 3])

    def test_eq_when_equal(self):
        self.assertEqual(Metadata(TestMetadata._TEST_VALUES), Metadata(TestMetadata._TEST_VALUES))

    def test_eq_when_not_eqal(self):
        self.assertNotEqual(Metadata(TestMetadata._TEST_VALUES), Metadata())

    def test_repr(self):
        string_representation = repr(self.metadata)
        self.assertTrue(isinstance(string_representation, str))

    def test_contains(self):
        self.assertIn(1, self.metadata)
        self.assertNotIn("a", self.metadata)

    def test_copy(self):
        self.assertEqual(copy.copy(self.metadata), self.metadata)

    def test_deepcopy(self):
        self.assertEqual(copy.deepcopy(self.metadata), self.metadata)


if __name__ == "__main__":
    unittest.main()
