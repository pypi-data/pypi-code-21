# Author: Michal Ciesielczyk
# Licence: MIT
import unittest
from time import sleep

from timeutils import timeit


class FunctionsTest(unittest.TestCase):
    def test_timeit(self):
        ftime = 0.1
        n = 5
        elapsed_time = timeit(sleep, number=n, args=[ftime])
        self.assertAlmostEqual(elapsed_time.total_seconds(), n * ftime, 2)

        rep = 3
        elapsed_time = timeit(sleep, number=n, repeat=rep, args=[ftime])
        self.assertEqual(len(elapsed_time), rep)
        for i in range(rep):
            self.assertAlmostEqual(elapsed_time[i - 1].total_seconds(),
                                   elapsed_time[i].total_seconds(), 2)


if __name__ == '__main__':
    unittest.main()
