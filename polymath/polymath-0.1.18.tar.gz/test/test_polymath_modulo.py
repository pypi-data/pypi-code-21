import unittest
from numpy import array, int8
from numpy.testing import assert_array_equal
import polymath

class Testpolymod(unittest.TestCase):

    def test_01(self):
        test_array = array([1], dtype=int8)
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([1], dtype=int8),
            "Polymath modulo of 1 % 101001101 fails"
        )

    def test_02(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([1], dtype=int8),
            "Polymath modulo of 00000001 % 101001101 fails"
        )

    def test_03(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 3], dtype=int8)
        f = array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([1], dtype=int8),
            "Polymath modulo of 3 % 101001101 fails"
        )

    def test_04(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        f          = array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([0], dtype=int8),
            "Polymath modulo of 00000000 % 101001101 fails"
        )

    def test_05(self):
        test_array = array([0], dtype=int8)
        f          = array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([0], dtype=int8),
            "Polymath modulo of 0 % 101001101 fails"
        )

    def test_06(self):
        test_array = array([1, 0, 1, 0, 0, 0, 1, 0, 0], dtype=int8)
        f =          array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([1, 0, 0, 1], dtype=int8),
            "Polymath modulo of 101000100 % 101001101 fails"
        )

    def test_07(self):
        test_array = array([0, 0, 0, 0, 0, 0, 1, 1, 1], dtype=int8)
        f =          array([1, 0, 1, 0, 0, 1, 1, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymod(test_array, f),
            array([1, 1, 1], dtype=int8),
            "Polymath modulo of 111 % 101001101 fails"
        )