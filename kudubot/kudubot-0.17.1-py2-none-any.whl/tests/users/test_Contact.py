u"""
Copyright 2015-2017 Hermann Krumrey

This file is part of kudubot.

kudubot is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

kudubot is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with kudubot.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import
import unittest
from kudubot.users.Contact import Contact


class UnitTests(unittest.TestCase):
    u"""
    Tests the Contact class
    """

    def setUp(self):
        u"""
        :return: None
        """
        pass

    def tearDown(self):
        u"""
        :return: None
        """
        pass

    def test_initialization(self):
        u"""
        Tests if the Contact class is initialized correctly

        :return: None
        """
        contact = Contact(1, u"A", u"B")
        self.assertEqual(contact.database_id, 1)
        self.assertEqual(contact.display_name, u"A")
        self.assertEqual(contact.address, u"B")
