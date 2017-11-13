import unittest
from numpy import array, int8
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestTransformID(unittest.TestCase):

    def test_01(self):
        k = 3
        input_test = array([
            [1, -1,  1, 1],
            [-1, -1,  1, 1]
            ], dtype=int8)
        result = array([
            [[1, -1,  1, 1],
             [1, -1,  1, 1],
             [1, -1,  1, 1]],
            [[-1, -1,  1, 1],
             [-1, -1,  1, 1],
             [-1, -1,  1, 1]]
            ], dtype=int8)
        assert_array_equal(
            ph.transform_id(input_test, k),
            result,
            "transform_id fails."
        )
