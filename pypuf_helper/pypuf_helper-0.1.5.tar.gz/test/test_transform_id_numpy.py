import unittest
from numpy import array, dot, transpose, tile, int8
from numpy.random import RandomState
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestTransformIDNumpy(unittest.TestCase):

    def test_01(self):
        n = 64
        k = 4
        random_instance = RandomState()
        challenges = [random_instance.choice((-1, +1), n) 
            for i in range(1000)]
        challenges = array(challenges, dtype=int8)
        
        ph_transformed_challenges = ph.transform_id(challenges, k)
        numpy_transformed_challenges = array([
                tile(c, (k, 1))
                for c in challenges
            ], dtype=int8)

        assert_array_equal(
            ph_transformed_challenges,
            numpy_transformed_challenges,
            "Comparison of transform_id with numpy fails."
        )