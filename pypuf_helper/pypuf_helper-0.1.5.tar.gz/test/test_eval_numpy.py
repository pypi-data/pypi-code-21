import unittest
from numpy import array, dot, transpose, sign, around, int8
from numpy.random import RandomState
from numpy.testing import assert_array_equal
import pypuf_helper as ph


class TestEvalNumpy(unittest.TestCase):

    def test_01(self):
        n = 64
        k = 4
        random_instance = RandomState()
        challenges = [random_instance.choice((-1, +1), n) 
            for i in range(1000)]
        challenges = array(challenges, dtype=int8)
        weights = random_instance.normal(loc=0, scale=1, size=(k, n))

        transformed_challenges = ph.transform_id(challenges, k)

        ph_solution = ph.eval(transformed_challenges, weights)
        
        numpy_solution = transpose(
                array([
                    dot(
                        transformed_challenges[:,l],
                        weights[l]
                    )
                    for l in range(k)
                ])
            )

        ph_solution = around(ph_solution, decimals=8)
        numpy_solution = around(numpy_solution, decimals=8)

        assert_array_equal(
            ph_solution,
            numpy_solution,
            "Comparison of eval with numpy fails."
        )
