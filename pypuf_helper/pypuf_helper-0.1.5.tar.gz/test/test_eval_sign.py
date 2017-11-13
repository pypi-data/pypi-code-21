import unittest
from numpy import array, int8
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestEvalSign(unittest.TestCase):

    def test_01(self):
        input_test = array([
            [[1, -1, -1], [1,  1,  1]],
            [[-1, -1,  1], [1, -1, -1]],
            [[1, -1,  1], [1, -1,  1]]
        ], dtype=int8)
        weights = array([
            [0.3, -0.2, 1.5],
            [-0.7, 2.5, -1]
        ])
        evaluated = array([
            [-1,  1],
            [1, -1],
            [1, -1]], dtype=int8)

        assert_array_equal(
            ph.eval_sign(input_test, weights),
            evaluated,
            "Evaluation with sign fails."
        )
