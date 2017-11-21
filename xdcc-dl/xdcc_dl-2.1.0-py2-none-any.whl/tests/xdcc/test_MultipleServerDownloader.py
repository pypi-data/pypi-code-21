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
from xdcc_dl.xdcc.MultipleServerDownloader import MultipleServerDownloader


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.isfile(u"1_test.txt"):
            os.remove(u"1_test.txt")
        if os.path.isfile(u"2_test.txt"):
            os.remove(u"2_test.txt")
        if os.path.isfile(u"3_test.txt"):
            os.remove(u"3_test.txt")

    def test_download_multiple_packs_same_server(self):

        progress = Progress(2)

        downloader = MultipleServerDownloader(u"random")

        downloader.download([
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1),
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)
        ], progress)

        self.assertTrue(os.path.isfile(u"1_test.txt"))
        self.assertTrue(os.path.isfile(u"3_test.txt"))

        self.assertEqual(progress.get_single_progress_percentage(), 100.0)
        self.assertEqual(progress.get_total_percentage(), 100.0)

    def test_download_multiple_packs_different_servers(self):

        progress = Progress(2)

        downloader = MultipleServerDownloader(u"random")

        downloader.download([
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
            XDCCPack(IrcServer(u"namibsun.net"), u"xdcc_servbot", 3)
        ], progress)

        self.assertTrue(os.path.isfile(u"2_test.txt"))
        self.assertTrue(os.path.isfile(u"3_test.txt"))

        self.assertEqual(progress.get_single_progress_percentage(), 100.0)
        self.assertEqual(progress.get_total_percentage(), 100.0)

    def test_quitting(self):

        packs = [XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1)]

        downloader = MultipleServerDownloader(u"random")
        downloader.quit()
        downloader.download(packs)
        downloader.quit()

        self.assertFalse(os.path.isfile(u"1_test.txt"))
