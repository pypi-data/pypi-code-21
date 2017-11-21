u"""
Copyright 2016-2017 Hermann Krumrey

This file is part of xdcc-dl.

xdcc-dl is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

xdcc-dl is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xdcc-dl.  If not, see <http://www.gnu.org/licenses/>.
"""

# imports
from __future__ import absolute_import
import unittest
from xdcc_dl.entities.User import User


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_user_constructor(self):

        user = User(u"username")
        self.assertEqual(user.get_name(), u"username")

    def test_random_username_generation(self):

        user_one = User(u"random")
        user_two = User()
        user_three = User(u"")

        self.assertNotEqual(u"random", user_one.get_name())
        self.assertNotEqual(u"", user_two.get_name())
        self.assertNotEqual(u"", user_three.get_name())

        self.assertNotEqual(user_one.get_name(), user_two.get_name())
        self.assertNotEqual(user_two.get_name(), user_three.get_name())
        self.assertNotEqual(user_three.get_name(), user_one.get_name())
