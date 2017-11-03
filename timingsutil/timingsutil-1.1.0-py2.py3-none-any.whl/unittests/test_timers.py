
import time
import unittest
import datetime
from timingsutil.timers import Timeout, Throttle, Stopwatch

__author__ = u'Oli Davis'
__copyright__ = u'Copyright (C) 2016 Oli Davis'


class TestConfiguration(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_timeout(self):

        timeout = Timeout(-1)
        self.assertLessEqual(timeout.seconds_remaining, 0)
        self.assertEqual(timeout.time_remaining, datetime.timedelta(seconds=0))
        self.assertTrue(timeout.expired)

        timeout = Timeout(0)
        self.assertEqual(timeout.seconds_remaining, 0)
        self.assertEqual(timeout.time_remaining, datetime.timedelta(seconds=0))
        self.assertTrue(timeout.expired)

        timeout = Timeout(5)
        self.assertGreaterEqual(timeout.seconds_remaining, 4)
        self.assertGreaterEqual(timeout.time_remaining, datetime.timedelta(seconds=4))
        self.assertFalse(timeout.expired)
        time.sleep(2)
        self.assertGreaterEqual(timeout.seconds_remaining, 2)
        self.assertGreaterEqual(timeout.time_remaining, datetime.timedelta(seconds=2))
        self.assertFalse(timeout.expired)
        time.sleep(3)
        self.assertTrue(timeout.expired)

    def test_timeout_wait(self):
        start_time = datetime.datetime.now()
        Timeout(5).wait()

        self.assertGreaterEqual(datetime.datetime.now(), start_time + datetime.timedelta(seconds=5))

        start_time = datetime.datetime.now()
        Timeout(0.5).wait()

        self.assertGreaterEqual(datetime.datetime.now(), start_time + datetime.timedelta(milliseconds=500))
        self.assertLess(datetime.datetime.now(), start_time + datetime.timedelta(milliseconds=600))

    def test_timeout_not_expired(self):

        start_time = datetime.datetime.now()
        iteration = 1
        timeout = Timeout(10)

        while not timeout.expired:
            time.sleep(1)
            self.assertGreaterEqual(timeout.elapsed_time, iteration)
            self.assertGreaterEqual(timeout.seconds_remaining, 0)
            iteration += 1

        self.assertGreaterEqual(datetime.datetime.now(), start_time + datetime.timedelta(seconds=10))

    def test_throttle(self):

        t = Throttle(2)

        self.assertEqual(t.interval, 0.5)

        for _ in range(5):
            current = datetime.datetime.now()
            t.wait()
            self.assertGreaterEqual(datetime.datetime.now(), current - datetime.timedelta(milliseconds=500))

    def test_stopwatch(self):

        stopwatch = Stopwatch()

        for _ in range(3):
            time.sleep(1)
            self.assertEqual(round(stopwatch.lap()), 1)

        self.assertEqual(round(stopwatch.stop()), 3)


if __name__ == u'__main__':
    unittest.main()
