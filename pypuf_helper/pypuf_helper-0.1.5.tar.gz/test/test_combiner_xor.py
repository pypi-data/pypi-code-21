import unittest
from numpy import array
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestCombinerXOR(unittest.TestCase):

    def test_signed_inputs(self):

        input_test = array([
            [1., -1.,  1., 1.],
            [-1., -1.,  1., 1.],
            [-1.,  1., -1., 1.],
            [-1., -1.,  1., -1.]
        ])
        result = array([-1., 1., 1., -1.])
        assert_array_equal(
            ph.combiner_xor(input_test),
            result,
            "XOR Combiner fails."
        )
