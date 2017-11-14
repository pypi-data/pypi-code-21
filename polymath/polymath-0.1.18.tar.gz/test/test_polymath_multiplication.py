import unittest
from numpy import array, int8
from numpy.testing import assert_array_equal
import polymath

class TestPolyMul(unittest.TestCase):

    def test_01(self):
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array1, test_array1),
            array([1], dtype=int8),
            "Polymath multiplication of 1*1 fails"
        )

    def test_02(self):
        test_array0 = array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array0, test_array0),
            array([0], dtype=int8),
            "Polymath multiplication of 0*0 fails"
        )

    def test_03(self):
        test_array0 = array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array0, test_array1),
            array([0], dtype=int8),
            "Polymath multiplication of 0*1 fails"
        )

    def test_04(self):
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        test_array0 = array([0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array1, test_array0),
            array([0], dtype=int8),
            "Polymath multiplication of 1*0 fails"
        )

    def test_05(self):
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        test_array2 = array([0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array1, test_array2),
            array([1, 1], dtype=int8),
            "Polymath multiplication of 1*11 fails"
        )

    def test_06(self):
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        test_array2 = array([0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array2, test_array1),
            array([1, 1], dtype=int8),
            "Polymath multiplication of 11*1 fails"
        )

    def test_07(self):
        test_array2 = array([0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array2, test_array2),
            array([1, 0, 1], dtype=int8),
            "Polymath multiplication of 11*11 fails"
        )

    def test_08(self):
        test_array1 = array([0, 0, 0, 0, 0, 1, 0, 1], dtype=int8)
        test_array2 = array([0, 0, 0, 0, 0, 0, 1, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array1, test_array2),
            array([1, 1, 1, 1], dtype=int8),
            "Polymath multiplication of 11*11 fails"
        )
        assert_array_equal(
            test_array1,
            array([0, 0, 0, 0, 0, 1, 0, 1], dtype=int8),
            "Original array changed"
        )
        assert_array_equal(
            test_array2,
            array([0, 0, 0, 0, 0, 0, 1, 1], dtype=int8),
            "Original array changed"
        )

    def test_09(self):
        test_array1 = array([0, 0, 0, 0, 0, 0, 0, 1], dtype=int8)
        test_array2 = array([1, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array2, test_array1),
            array([1, 0, 0, 0, 0, 0, 0, 0], dtype=int8),
            "Polymath multiplication of 10000000*1 fails"
        )

    def test_10(self):
        test_array = array([1, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8),
            "Polymath multiplication of 10000000*10000000 fails"
        )

    def test_11(self):
        test_array = array([0, 0, 1, 0, 1, 0, 1, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0], dtype=int8),
            "Polymath multiplication of 101010*101010 fails"
        )
        assert_array_equal(
            test_array,
            array([0, 0, 1, 0, 1, 0, 1, 0], dtype=int8),
            "Original array changed"
        )

    def test_12(self):
        test_array = array([0, 0, 0, 1, 1, 0, 1, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1, 0, 1, 0, 0, 0, 1, 0, 0], dtype=int8),
            "Polymath multiplication of 11010*11010 fails"
        )

    def test_13(self):
        test_array1 = array([0, 0, 0, 1, 1, 0, 1, 0], dtype=int8)
        test_array2 = array([0, 0, 0, 0, 1, 0, 0, 1], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array2, test_array1),
            array([1, 1, 0, 0, 1, 0, 1, 0], dtype=int8),
            "Polymath multiplication of 1001*11010 fails"
        )

    def test_14(self):
        test_array = array([0, 0, 0, 0, 0, 0, 0, 3], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1], dtype=int8),
            "Polymath read only last bit fails"
        )

    def test_15(self):
        test_array = array([0, 0, 0, 0, 0, 0, 5, 3], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1, 0, 1], dtype=int8),
            "Polymath read only last bit fails"
        )

    def test_16(self):
        test_array = array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
                            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        assert_array_equal(
            polymath.polymul(test_array, test_array),
            array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8),
            "Polymath multiplication of x^32 * x^32 fails."
        )

    def test_17(self):
        test_array1 = array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        test_array2 = array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        
        assert_array_equal(
            polymath.polymul(test_array1, test_array2),
            array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], dtype=int8)
        )
