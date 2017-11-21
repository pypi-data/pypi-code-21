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
import os
import unittest
from xdcc_dl.entities.IrcServer import IrcServer
from xdcc_dl.entities.XDCCPack import XDCCPack, xdcc_packs_from_xdcc_message


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.pack = XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1)

    def tearDown(self):
        pass

    def test_getters(self):

        self.assertEqual(self.pack.get_packnumber(), 1)
        self.assertEqual(self.pack.get_bot(), u"xdcc_servbot")
        self.assertEqual(self.pack.get_filename(), u"")
        self.assertEqual(self.pack.get_size(), 0)
        self.assertEqual(self.pack.get_server().get_address(),
                         u"irc.namibsun.net")
        self.assertEqual(self.pack.get_filepath(), os.getcwdu() + os.sep)
        self.assertEqual(self.pack.get_request_message(), u"xdcc send #1")

    def test_setting_filename(self):

        self.pack.set_filename(u"test")
        self.assertEqual(self.pack.get_filename(), u"test")
        self.assertEqual(
            self.pack.get_filepath(), os.path.join(os.getcwdu(), u"test"))

        self.pack.set_filename(u"something")
        self.assertEqual(self.pack.get_filename(), u"test")
        self.assertEqual(
            self.pack.get_filepath(), os.path.join(os.getcwdu(), u"test"))

        self.pack.set_filename(u"something", override=True)
        self.assertEqual(self.pack.get_filename(), u"something")
        self.assertEqual(
            self.pack.get_filepath(), os.path.join(os.getcwdu(), u"something"))

        self.pack.set_filename(u"something_else.txt")
        self.assertEqual(self.pack.get_filename(), u"something.txt")
        self.assertEqual(self.pack.get_filepath(),
                         os.path.join(os.getcwdu(), u"something.txt"))

        self.pack.set_filename(u"something_else.txt")
        self.assertEqual(self.pack.get_filename(), u"something.txt")
        self.assertEqual(self.pack.get_filepath(),
                         os.path.join(os.getcwdu(), u"something.txt"))

        self.pack.set_filename(u"something_else.mkv")
        self.assertEqual(self.pack.get_filename(), u"something.txt.mkv")
        self.assertEqual(self.pack.get_filepath(),
                         os.path.join(os.getcwdu(), u"something.txt.mkv"))

        self.pack.set_directory(os.path.join(os.getcwdu(), u"test"))
        self.assertEqual(self.pack.get_filename(), u"something.txt.mkv")
        self.assertEqual(
            self.pack.get_filepath(),
            os.path.join(os.getcwdu(), u"test", u"something.txt.mkv")
        )

    def test_original_filename_check(self):

        self.assertTrue(self.pack.is_filename_valid(u"the_original"))
        self.assertTrue(self.pack.is_filename_valid(u"not_the_original"))
        self.pack.set_original_filename(u"the_original")
        self.assertTrue(self.pack.is_filename_valid(u"the_original"))
        self.assertFalse(self.pack.is_filename_valid(u"not_the_original"))

    def test_request_message(self):
        self.assertEqual(self.pack.get_request_message(), u"xdcc send #1")
        self.assertEqual(self.pack.get_request_message(full=True),
                         u"/msg xdcc_servbot xdcc send #1")

    def test_generating_from_xdcc_message_single(self):

        packs = xdcc_packs_from_xdcc_message(
            u"/msg xdcc_servbot xdcc send #1", u"testdir", u"irc.namibsun.net")
        self.assertEqual(len(packs), 1)
        pack = packs[0]

        self.assertEqual(pack.get_packnumber(), 1)
        self.assertEqual(pack.get_bot(), u"xdcc_servbot")
        self.assertEqual(pack.get_server().get_address(), u"irc.namibsun.net")
        self.assertEqual(pack.get_filepath(), u"testdir" + os.sep)
        self.assertTrue(
            pack.get_request_message() in u"/msg xdcc_servbot xdcc send #1"
        )

    def test_generating_from_xdcc_message_range(self):

        packs = xdcc_packs_from_xdcc_message(
            u"/msg xdcc_servbot xdcc send #1-100"
        )
        self.assertEqual(len(packs), 100)

        for i, pack in enumerate(packs):
            self.assertEqual(pack.get_packnumber(), i + 1)
            self.assertEqual(pack.get_server().get_address(), u"irc.rizon.net")
            self.assertEqual(pack.get_filepath(), os.getcwdu() + os.sep)

    def test_generating_from_xdcc_message_range_with_jumps(self):

        packs = xdcc_packs_from_xdcc_message(
            u"/msg xdcc_servbot xdcc send #1-100,2"
        )
        self.assertEqual(len(packs), 50)

        i = 1
        for pack in packs:
            self.assertEqual(pack.get_packnumber(), i)
            i += 2

    def test_generating_invalid_xdcc_message(self):

        packs = xdcc_packs_from_xdcc_message(u"randomnonesense")
        self.assertEqual(len(packs), 0)
