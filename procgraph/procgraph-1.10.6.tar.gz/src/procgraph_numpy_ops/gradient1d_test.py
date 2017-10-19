import unittest
from numpy.testing import assert_array_almost_equal

from .gradient1d import gradient1d


class TestGradient(unittest.TestCase):

    def testInvalid(self):
        self.assertRaises(ValueError, gradient1d, [0])
        self.assertRaises(ValueError, gradient1d, [0, 0])

    def testSimply(self):
        examples = [
            ([0, 0, 0], [0, 0, 0]),
            ([1, 1, 1], [0, 0, 0]),
            ([1, 2, 3], [1, 1, 1])
        ]

        for f, gf in examples:
            g = gradient1d(f)

            assert_array_almost_equal(g, gf)
