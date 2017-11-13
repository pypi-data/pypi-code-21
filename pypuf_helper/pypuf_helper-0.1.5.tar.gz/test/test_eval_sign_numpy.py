import unittest
from numpy import array, dot, transpose, sign, int8
from numpy.random import RandomState
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestEvalSignNumpy(unittest.TestCase):

    def test_01(self):
        n = 64
        k = 4
        random_instance = RandomState()
        challenges = [random_instance.choice((-1, +1), n) 
            for i in range(1000)]
        challenges = array(challenges, dtype=int8)
        weights = random_instance.normal(loc=0, scale=1, size=(k, n))

        transformed_challenges = ph.transform_id(challenges, k)

        ph_solution = ph.eval_sign(transformed_challenges, weights)
        
        numpy_solution = sign(
            transpose(
                array([
                    dot(
                        transformed_challenges[:,l],
                        weights[l]
                    )
                    for l in range(k)
                ])
            )).astype(int)

        numpy_solution = array(numpy_solution, dtype=int8, copy=True)

        assert_array_equal(
            ph_solution,
            numpy_solution,
            "Comparison of eval_sign with numpy fails."
        )
