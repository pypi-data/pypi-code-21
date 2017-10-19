# Author: Michal Ciesielczyk
# Licence: MIT
import unittest

from timeutils.timespan import TimeSpan


class TimeSpanTest(unittest.TestCase):
    def eq_test(self):
        self.assertNotEqual(TimeSpan(0), None)
        self.assertNotEqual(TimeSpan(0), 0)
        self.assertEqual(TimeSpan(0), TimeSpan(0))
        self.assertEqual(TimeSpan(1.5), TimeSpan(1.5))
        self.assertNotEqual(TimeSpan(10.4), TimeSpan(0.5))
        self.assertNotEqual(TimeSpan(0), TimeSpan(0.5))

    def compare_test(self):
        self.assertLess(TimeSpan(0), TimeSpan(1))
        self.assertLessEqual(TimeSpan(0), TimeSpan(1))
        self.assertLessEqual(TimeSpan(1), TimeSpan(1))
        self.assertGreater(TimeSpan(1), TimeSpan(0))
        self.assertGreaterEqual(TimeSpan(1), TimeSpan(0))
        self.assertGreaterEqual(TimeSpan(1), TimeSpan(1))

    def add_test(self):
        a = TimeSpan(5)
        b = TimeSpan(3)

        self.assertEqual((a + b).total_seconds(), 8)
        self.assertNotEqual((a + b).total_seconds(), 5)

        self.assertEqual(a + b, TimeSpan(8))
        self.assertNotEqual(a + b, TimeSpan(3))

    def subtract_test(self):
        a = TimeSpan(5)
        b = TimeSpan(3)

        self.assertEqual((a - b).total_seconds(), 2)
        self.assertNotEqual((a - b).total_seconds(), 5)

        self.assertEqual(a - b, TimeSpan(2))
        self.assertNotEqual(a - b, TimeSpan(5))

    def total_test(self):
        v = 12345
        self.assertEqual(TimeSpan(v).total_seconds(), v)
        self.assertEqual(TimeSpan(minutes=v).total_minutes(), v)
        self.assertEqual(TimeSpan(hours=v).total_hours(), v)
        self.assertEqual(TimeSpan(milliseconds=v).total_milliseconds(), v)

    def test_human_str(self):
        ts = TimeSpan(0)
        self.assertEqual(ts.human_str(), "0 ms")
        self.assertEqual(ts.human_str(significant_digits=4),
                         "0.0000 milliseconds")

        ts = TimeSpan(0.55)
        self.assertEqual(ts.human_str(), "550 ms")
        self.assertEqual(ts.human_str(significant_digits=3),
                         "550.000 milliseconds")

        ts = TimeSpan(1.5)
        self.assertEqual(ts.human_str(), "1 sec")
        self.assertEqual(ts.human_str(significant_digits=2), "1.50 seconds")

        ts = TimeSpan(100)
        self.assertEqual(ts.human_str(), "1 min, 40 secs")
        self.assertEqual(ts.human_str(significant_digits=3), "1.667 minutes")

        ts = TimeSpan(360)
        self.assertEqual(ts.human_str(), "6 mins, 0 secs")
        self.assertEqual(ts.human_str(significant_digits=0), "6 minutes")

        ts = TimeSpan(10000000)
        self.assertEqual(ts.human_str(), "115 days, 17 hours, 46 mins, 40 secs")
        self.assertEqual(ts.human_str(significant_digits=3), "115.741 days")

        ts = TimeSpan(250.5)
        self.assertEqual(ts.human_str(trim_zeros=False),
                         "0 days, 0 hours, 4 mins, 10 secs")
        self.assertEqual(ts.human_str(significant_digits=3), "4.175 minutes")

        ts = TimeSpan(90100.4534)
        self.assertEqual(ts.human_str(), "1 day, 1 hour, 1 min, 40 secs")
        self.assertEqual(ts.human_str(significant_digits=5), "1.04283 days")

    def test_str(self):
        ts = TimeSpan(1000.1234567)
        self.assertEqual(str(ts), "0:16:40.123457")

        ts = TimeSpan(21000.4534)
        self.assertEqual(str(ts), "5:50:00.453400")

        ts = TimeSpan(321000.4534)
        self.assertEqual(str(ts), "3 days, 17:10:00.453400")

        ts = TimeSpan(263400.4534)
        self.assertEqual(str(ts), "3 days, 1:10:00.453400")

        ts = TimeSpan(266500.4534)
        self.assertEqual(str(ts), "3 days, 2:01:40.453400")

        ts = TimeSpan(86400000)
        self.assertEqual(str(ts), "1000 days, 0:00:00")


if __name__ == '__main__':
    unittest.main()
