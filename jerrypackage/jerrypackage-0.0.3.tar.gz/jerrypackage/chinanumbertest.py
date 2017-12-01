import chinanumber
import unittest


class KnownValues(unittest.TestCase):
    known_values = ((0, '零'),
                    (1, '壹'),
                    (2, '贰'),
                    (3, '叁'),
                    (4, '肆'),
                    (5, '伍'),
                    (6, '陆'),
                    (7, '柒'),
                    (8, '捌'),
                    (9, '玖'),
                    (10, '壹拾'),
                    (100, '壹佰'),
                    (1000, '壹仟'),
                    (10000, '壹萬'),
                    (100000000, '壹亿'),
                    (1000000000000, '壹兆'),
                    (312, '叁佰壹拾贰'))

    def test_to_china_known_values(self):
        """ to_china should give known result with known input """
        for integer, numeral in self.known_values:
            result = chinanumber.to_china(integer)
            self.assertEqual(numeral, result)

    def test_from_china_known_values(self):
        """from_china should give known result with known input """
        for integer, numeral in self.known_values:
            result = chinanumber.from_china(numeral)
            self.assertEqual(integer, result)


# TODO
class ToChinaBadInput(unittest.TestCase):
    def test_too_large(self):
        """ to_china should fail with large input """
        self.assertRaises(chinanumber.OutOfRangeError, chinanumber.to_china, 4000)

    def test_zero(self):
        """ to_china should fail with 0 input """
        self.assertRaises(chinanumber.OutOfRangeError, chinanumber.to_china, 0)

    def test_negative(self):
        """ to_china should fail with negative input """
        self.assertRaises(chinanumber.OutOfRangeError, chinanumber.to_china, -1)

    def test_non_integer(self):
        """ to_china should fail with non-integer input """
        self.assertRaises(chinanumber.NotIntegerError, chinanumber.to_china, 0.5)


# TODO
class RoundtripCheck(unittest.TestCase):
    def test_roundtrip(self):
        """ from_china(to_china(n)) == n for all n """
        for integer in range(1, 4000):
            numeral = chinanumber.to_china(integer)
            result = chinanumber.from_china(numeral)
            self.assertEqual(integer, result)


# TODO
class FromRomanBadInput(unittest.TestCase):
    def test_too_many_repeated_numerals(self):
        """ from_china should fail with too many repeated numerals"""
        for s in ('MMMM', 'DD', 'CCCC', 'LL', 'XXXX', 'VV', 'IIII'):
            self.assertRaises(chinanumber.InvalidRomanNumeralError, chinanumber.from_china, s)

    def test_repeated_pairs(self):
        """ from_china should fail with repeated pairs of numerals"""
        for s in ('CMCM', 'CDCD', 'XCXC', 'XLXL', 'IXIX', 'IVIV'):
            self.assertRaises(chinanumber.InvalidRomanNumeralError, chinanumber.from_china, s)

    def test_malformed_antecedents(self):
        """ from_china should fail with malformed antecedents"""
        for s in ('IIMXCC', 'VX', 'DCM', 'CMM', 'IXIV', 'MCMC', 'XCX', 'IVI', 'LM', 'LD', 'LC'):
            self.assertRaises(chinanumber.InvalidRomanNumeralError, chinanumber.from_china, s)

    def test_blank(self):
        """ from_china should fail with blank string"""
        self.assertRaises(chinanumber.InvalidRomanNumeralError, chinanumber.from_china, '')


if __name__ == '__main__':
    unittest.main()
