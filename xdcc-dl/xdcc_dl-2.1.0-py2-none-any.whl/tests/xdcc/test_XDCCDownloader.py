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
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.Progress import Progress
from xdcc_dl.entities.IrcServer import IrcServer
from xdcc_dl.xdcc.XDCCDownloader import XDCCDownloader
from xdcc_dl.xdcc.layers.helpers.BotChannelMapper import BotChannelMapper


class UnitTests(unittest.TestCase):

    def setUp(self):
        self.downloader = XDCCDownloader(u"irc.namibsun.net", u"random")

    def tearDown(self):
        if os.path.isfile(u"1_test.txt"):
            os.remove(u"1_test.txt")
        if os.path.isfile(u"2_test.txt"):
            os.remove(u"2_test.txt")
        if os.path.isfile(u"3_test.txt"):
            os.remove(u"3_test.txt")

    def test_download_multiple_packs(self):

        progress = Progress(2)

        packs = [XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
                 XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)]

        results = self.downloader.download(packs, progress)

        for pack in results:
            self.assertTrue(os.path.isfile(pack.get_filepath()))
            self.assertEqual(results[pack], u"OK")

        self.assertEqual(progress.get_single_progress_percentage(), 100.0)
        self.assertEqual(progress.get_total_percentage(), 100.0)

    def test_bot_not_found(self):

        pack = XDCCPack(IrcServer(u"irc.namibsun.net"), u"nosuchbot", 2)
        results = self.downloader.download([pack])

        self.assertFalse(os.path.isfile(pack.get_filepath()))
        self.assertEqual(results[pack], u"BOTNOTFOUND")

    def test_file_existed(self):

        pack = XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2)

        self.downloader.download([pack])
        self.assertTrue(os.path.isfile(pack.get_filepath()))

        results = self.downloader.download([pack])
        self.assertTrue(os.path.isfile(pack.get_filepath()))
        self.assertEqual(results[pack], u"EXISTED")

    def test_incorrect_file_sent(self):

        pack = XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2)
        pack.set_original_filename(u"something_else.txt")

        results = self.downloader.download([pack])
        self.assertFalse(os.path.isfile(pack.get_filepath()))
        self.assertEqual(results[pack], u"INCORRECT")

    def test_network_error(self):

        pack = XDCCPack(IrcServer(u"gitlab.namibsun.net"), u"xdcc_servbot", 2)
        results = XDCCDownloader(u"gitlab.namibsun.net", u"random").\
            download([pack])
        self.assertEqual(results[pack], u"NETWORKERROR")

    def test_different_servers(self):

        packs_one = XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2)
        pack_two = XDCCPack(IrcServer(u"irc.rizon.net"), u"xdcc_servbot", 2)

        results = self.downloader.download([packs_one, pack_two])

        self.assertEqual(results[packs_one], u"OK")
        self.assertEqual(results[pack_two], u"OTHERSERVER")

    # HelloKitty doesn't exist anymore
    # def test_invalid_whois_query(self):
    #
    #    BotChannelMapper.bot_channel_map = {}
    #
    #    pack = XDCCPack(IrcServer("irc.rizon.net"), "HelloKitty", 1)
    #    results = XDCCDownloader("irc.rizon.net", "random").download([pack])
    #    self.assertEqual(results[pack], "CHANNELJOINFAIL")
