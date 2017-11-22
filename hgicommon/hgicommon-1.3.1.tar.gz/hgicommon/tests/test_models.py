"""
Legalese
--------
Copyright (c) 2015, 2016 Genome Research Ltd.

Author: Colin Nolan <cn13@sanger.ac.uk>

This file is part of HGI's common Python library

This program is free software: you can redistribute it and/or modify it
under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation; either version 3 of the License, or (at
your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.
"""
import copy
import unittest
from datetime import date

from hgicommon.tests._stubs import StubModel


class TestModel(unittest.TestCase):
    """
    Test cases for `Model`.
    """
    def setUp(self):
        self._model = StubModel()
        self._model.property_1 = 1
        self._model.property_2 = "a"
        self._model.property_3 = [i for i in range(1000)]
        self._model.property_4 = set([i for i in range(1000)])

    def test_equal_non_nullity(self):
        self.assertNotEqual(self._model, None)

    def test_equal_different_type(self):
        self.assertNotEqual(self._model, date)

    def test_equal_reflexivity(self):
        model = self._model
        self.assertEqual(model, model)

    def test_equal_symmetry(self):
        model1 = self._model
        model2 = copy.copy(self._model)
        self.assertEqual(model1, model2)
        self.assertEqual(model2, model1)

    def test_equal_transitivity(self):
        model1 = self._model
        model2 = copy.copy(self._model)
        model3 = copy.copy(self._model)
        self.assertEqual(model1, model2)
        self.assertEqual(model2, model3)
        self.assertEqual(model1, model3)

    def test_can_get_string_representation(self):
        string_representation = str(self._model)
        self.assertTrue(isinstance(string_representation, str))

    def test_can_get_representation(self):
        string_representation = repr(self._model)
        self.assertTrue(isinstance(string_representation, str))


if __name__ == "__main__":
    unittest.main()
