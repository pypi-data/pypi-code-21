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

from kudubot.entities.Message import Message
from kudubot.users.Contact import Contact


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_creating_message(self):

        message = Message(u"title", u"body", Contact(-1, u"A", u"Add"),
                          Contact(-2, u"B", u"Badd"), Contact(-3, u"C", u"Cadd"),
                          timestamp=1.0)

        self.assertEqual(message.message_title, u"title")
        self.assertEqual(message.message_body, u"body")
        self.assertEqual(message.receiver.display_name, u"A")
        self.assertEqual(message.sender.display_name, u"B")
        self.assertEqual(message.sender_group.display_name, u"C")
        self.assertEqual(message.timestamp, 1.0)
