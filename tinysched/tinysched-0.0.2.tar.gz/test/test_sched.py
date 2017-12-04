import unittest
import time
from datetime import timedelta

from tinysched import scheduler


class TestSched(unittest.TestCase):
    def setUp(self):
        self.count = 0

    def test_repeat(self):
        def foo():
            self.count += 1

        repeats = 3
        scheduler.repeat(self.inc_counter, timedelta(seconds=0), max_repeats=repeats)
        time.sleep(0.1)
        self.assertEqual(self.count, repeats)

    def test_interval(self):
        repeats = 3
        delay = 0.01
        scheduler.repeat(self.inc_counter, timedelta(seconds=delay), max_repeats=repeats)
        for r in range(repeats):
            self.assertLessEqual(self.count, r + 1)
            time.sleep(delay)

    def test_cancel(self):
        delay = 0.01
        cancel_after_n = 10
        cancel = scheduler.repeat(self.inc_counter, timedelta(seconds=delay))
        time.sleep(delay * cancel_after_n)
        cancel()
        self.assertLessEqual(self.count, cancel_after_n)

    def inc_counter(self):
        self.count += 1
