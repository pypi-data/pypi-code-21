u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of toktokkie.

toktokkie is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

toktokkie is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with toktokkie.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
import unittest
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure


class GenericProcedureUnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_standard_values(self):
        self.assertEqual(GenericProcedure.get_icon_file(u"AnyDir"), None)
        self.assertTrue(GenericProcedure.is_applicable())
        GenericProcedure.iconize(u"Something", u"Some Icon")
        self.assertEqual(GenericProcedure.get_procedure_name(), u"generic")
