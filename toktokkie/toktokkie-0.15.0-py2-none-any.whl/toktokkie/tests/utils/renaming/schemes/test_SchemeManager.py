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
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager


class SchemeManagerUnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_scheme_name_passing(self):
        all_schemes = SchemeManager.get_all_schemes()
        scheme_names = SchemeManager.get_scheme_names()

        for scheme in all_schemes:
            self.assertTrue(scheme.get_scheme_name() in scheme_names)
            self.assertEqual(scheme, SchemeManager.get_scheme_from_scheme_name(
                scheme.get_scheme_name()))

    def test_invalid_scheme_name(self):
        self.assertEqual(
            SchemeManager.get_scheme_from_scheme_name(u"SomeInvalidName"), None
        )
