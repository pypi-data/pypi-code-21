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
from toktokkie.utils.renaming.schemes.GenericScheme import GenericScheme


class GenericSchemeUnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_get_tvdb_episode_name(self):
        self.assertEqual(
            GenericScheme.get_tvdb_episode_name(u"Game of Thrones", 1, 1),
            u"Winter Is Coming")
        self.assertEqual(
            GenericScheme.get_tvdb_episode_name(u"Game of Thrones", 1, 11),
            u"Episode 11")
        self.assertEqual(
            GenericScheme.get_tvdb_episode_name(u"Show does not exist", 1, 1),
            u"Episode 1")
        self.assertEqual(
            GenericScheme.get_tvdb_episode_name(u"Game of Thrones", -1, 1),
            u"Episode 1")
        self.assertEqual(
            GenericScheme.get_tvdb_episode_name(u"Game of Thrones", 1, -1),
            u"Episode -1")

    def abstract_method(self):
        try:
            GenericScheme(u"", 0, 0).apply_scheme()
            self.assertTrue(False)
        except NotImplementedError:
            pass

        try:
            GenericScheme(u"", 0, 0).generate_episode_name()
            self.assertTrue(False)
        except NotImplementedError:
            pass
