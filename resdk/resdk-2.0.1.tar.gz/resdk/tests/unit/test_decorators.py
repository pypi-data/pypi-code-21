"""
Unit tests for resdk/utils/decorators.py file.
"""
# pylint: disable=missing-docstring, protected-access

import unittest

from resdk.utils.decorators import return_first_element


class TestDecorators(unittest.TestCase):

    def test_return_first_element(self):

        @return_first_element
        def test_function():
            return [1]

        self.assertEqual(test_function(), 1)

        @return_first_element
        def test_function_2():
            return [1, 2]

        with self.assertRaises(RuntimeError):
            test_function_2()

        @return_first_element
        def test_function_3():
            return 1

        with self.assertRaises(TypeError):
            test_function_3()
