import unittest

from velenxc.const import ConstInstance, ConstantError, ConstantCaseError


class ConstTestCase(unittest.TestCase):
    def test_should_not_be_able_to_change_constant(self):
        with self.failUnlessRaises(ConstantError):
            ConstInstance.COMMA_CHAR = ';'

    def test_constant_name_should_be_upper_case(self):
        with self.failUnlessRaises(ConstantCaseError):
            ConstInstance.comma_char2 = ','

    def test_constant_name_should_exist(self):
        self.assertEqual(None, ConstInstance.comma_char2)

    def test_normal_constant_should_be_accessible(self):
        self.assertEqual(',', ConstInstance.COMMA_CHAR)
