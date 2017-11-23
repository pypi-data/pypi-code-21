from unittest import TestCase
from unittest.mock import MagicMock
from pyOptional.optional import Optional
from pyOptional.exceptions import NoneValueError


class TestOptional(TestCase):
    def test_should_get_value(self):
        # given
        opt = Optional('ABC')

        # when
        result = opt.get()

        # then
        self.assertEqual(result, 'ABC')

    def test_should_raise_exception_when_get_on_empty(self):
        # given
        opt = Optional(None)

        # when
        with self.assertRaisesRegex(NoneValueError, 'Called get on empty optional'):
            opt.get()

    def test_should_get_value_when_exists(self):
        # given
        opt = Optional('ABC')

        # when
        result = opt.get_or_else('XYZ')

        # then
        self.assertEqual(result, 'ABC')

    def test_should_get_default_value_when_empty(self):
        # given
        opt = Optional(None)

        # when
        result = opt.get_or_else('XYZ')

        # then
        self.assertEqual(result, 'XYZ')

    def test_should_return_true_when_present(self):
        # given
        opt = Optional('ABC')

        # when
        result = opt.is_present()

        # then
        self.assertTrue(result)

    def test_should_return_false_when_empty(self):
        # given
        opt = Optional(None)

        # when
        result = opt.is_present()

        # then
        self.assertFalse(result)

    def test_should_return_value_when_exists(self):
        # given
        opt = Optional('ABC')

        # when
        result = opt.get_or_else_get(lambda: 'XYZ')

        # then
        self.assertEqual(result, 'ABC')

    def test_should_evaluate_default_expression_when_empty(self):
        # given
        opt = Optional(None)

        # when
        result = opt.get_or_else_get(lambda: 'XYZ')

        # then
        self.assertEqual(result, 'XYZ')

    def test_should_return_value_instead_of_exception_when_exists(self):
        # given
        opt = Optional('ABC')

        # when
        result = opt.get_or_raise(IOError, 'Some message')

        # then
        self.assertEqual(result, 'ABC')

    def test_should_raise_selected_exception_when_empty(self):
        # given
        opt = Optional(None)

        # when
        with self.assertRaisesRegex(ArithmeticError, 'Some message'):
            opt.get_or_raise(ArithmeticError, 'Some message')

    def test_should_transform_value_when_exists(self):
        # given
        opt = Optional(18)

        # when
        result = opt.map(lambda val: val * 3)

        # then
        self.assertTrue(result.is_present())
        self.assertEqual(result.get(), 54)

    def test_should_transform_value_of_nested_optional(self):
        # given
        opt = Optional(Optional(18))

        # when
        result = opt.map(lambda val: val.is_present())

        # then
        self.assertTrue(result.is_present())
        self.assertTrue(result.get())

    def test_should_return_empty_optional_when_not_exists(self):
        # given
        opt = Optional(None)

        # when
        result = opt.map(lambda val: val * 3)

        # then
        self.assertFalse(result.is_present())

    def test_should_transform_nested_optional(self):
        # given
        opt = Optional(Optional(Optional(Optional(21))))

        # when
        result = opt.flat_map(lambda val: val * 3)

        # then
        self.assertTrue(result)
        self.assertEqual(result.get(), 63)

    def test_should_get_empty_if_nested_optional_empty(self):
        # given
        opt = Optional(Optional(Optional(Optional(None))))

        # when
        result = opt.flat_map(lambda val: val * 3)

        # then
        self.assertFalse(result.is_present())

    def test_should_true_if_non_empty(self):
        # when
        opt = Optional('ABC')

        # then
        self.assertTrue(opt)

    def test_should_false_if_not_empty(self):
        # when
        opt = Optional(None)

        # then
        self.assertFalse(opt)

    def test_should_call_action_when_present(self):
        # given
        opt = Optional('ABC')
        dest = MagicMock()

        # when
        opt.if_present(dest.func)

        # then
        dest.func.assert_called_once_with('ABC')

    def test_should_not_call_action_when_not_present(self):
        # given
        opt = Optional(None)
        dest = MagicMock()

        # when
        opt.if_present(dest.func)

        # then
        dest.func.assert_not_called()

    def test_should_return_true_for_equal_optionals(self):
        # given
        opt1 = Optional('ABC')
        opt2 = Optional('ABC')

        # when
        result = opt1 == opt2

        # then
        self.assertTrue(result)

    def test_should_return_true_for_both_empty_optionals(self):
        # given
        opt1 = Optional(None)
        opt2 = Optional(None)

        # when
        result = opt1 == opt2

        # then
        self.assertTrue(result)

    def test_should_return_false_for_non_equal_optionals(self):
        # given
        opt1 = Optional('ABD')
        opt2 = Optional('ABC')

        # when
        result = opt1 == opt2

        # then
        self.assertFalse(result)

    def test_should_return_false_for_optional_and_value(self):
        # given
        val = "ABC"
        opt = Optional(val)

        # when
        result = val == opt

        # then
        self.assertFalse(result)
