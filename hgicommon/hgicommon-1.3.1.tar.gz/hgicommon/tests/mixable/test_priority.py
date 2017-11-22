"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

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
import unittest
from queue import PriorityQueue

from hgicommon.mixable import Priority


class TestPriority(unittest.TestCase):
    """
    Test cases for `Priority`.
    """
    class _MockPriority(Priority):
        pass

    def setUp(self):
        self.low_priority = TestPriority._MockPriority(Priority.MIN_PRIORITY)
        self.medium_priority = TestPriority._MockPriority(Priority.get_lower_priority_value(Priority.MAX_PRIORITY))
        self.high_priority = TestPriority._MockPriority(Priority.MAX_PRIORITY)

    def test_get_lower_priority_value(self):
        lower = Priority.get_lower_priority_value(Priority.MAX_PRIORITY)
        self.assertLess(abs(lower - Priority.MIN_PRIORITY), abs(Priority.MAX_PRIORITY - Priority.MIN_PRIORITY))

    def test_get_lower_priority_value_if_already_minimum(self):
        self.assertRaises(ValueError, Priority.get_lower_priority_value, Priority.MIN_PRIORITY)

    def test_get_higher_priority_value(self):
        higher = Priority.get_higher_priority_value(Priority.MIN_PRIORITY)
        self.assertLess(abs(higher - Priority.MIN_PRIORITY), abs(Priority.MAX_PRIORITY - Priority.MIN_PRIORITY))

    def test_get_higher_priority_value_if_already_maximum(self):
        self.assertRaises(ValueError, Priority.get_higher_priority_value, Priority.MAX_PRIORITY)

    def test_work_in_priority_queue(self):
        queue = PriorityQueue()
        priorities = [self.medium_priority, self.low_priority, self.high_priority]

        for priority in priorities:
            queue.put(priority)

        self.assertListEqual(sorted(priorities), [self.high_priority, self.medium_priority, self.low_priority])
        self.assertEqual(queue.get(), self.high_priority)
        self.assertEqual(queue.get(), self.medium_priority)
        self.assertEqual(queue.get(), self.low_priority)


if __name__ == "__main__":
    unittest.main()
