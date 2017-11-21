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
from __future__ import with_statement
from __future__ import absolute_import
import os
import unittest
from xdcc_dl.entities.Progress import Progress
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.xdcc.layers.xdcc.DownloadHandler import DownloadHandler
from io import open


class UnitTests(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        if os.path.isfile(u"testfile.mkv"):
            os.remove(u"testfile.mkv")
        if os.path.isfile(u"1_test.txt"):
            os.remove(u"1_test.txt")
        if os.path.isfile(u"2_test.txt"):
            os.remove(u"2_test.txt")
        if os.path.isfile(u"3_test.txt"):
            os.remove(u"3_test.txt")

    def test_incomplete_download(self):

        class Tester(DownloadHandler):

            download_incomplete_check = False
            download_completed_check = True

            def on_welcome(self, conn, event):

                self.progress = Progress(1)

                self.file = open(u"testfile.mkv", u'wb')
                self.file.write("test")
                self.filesize = 10000000

                self.current_pack = XDCCPack(self.server, u"xdcc_servbot", 1)
                self.pack_queue = []

                self.logger.log = self.logging_handler

                self.on_dcc_disconnect(conn, event)

            # noinspection PyUnusedLocal
            def logging_handler(self, string, formatting,
                                carriage_return=None):
                if string == u"Download Incomplete, Trying again.":
                    self.download_incomplete_check = True
                elif u"Download completed in" in string:
                    self.download_completed_check = True
                else:
                    print string

        client = Tester(u"irc.namibsun.net", u"random")
        client.start()

        self.assertTrue(os.path.isfile(u"1_test.txt"))
        self.assertTrue(client.download_completed_check)
        self.assertTrue(client.download_incomplete_check)

    # XDCCInitator-related tests

    def test_extended_privnotice(self):

        class Tester(DownloadHandler):

            def on_welcome(self, conn, event):

                self.current_pack = XDCCPack(self.server, u"xdcc_servbot", 3)
                self.pack_queue = []
                self.progress = Progress(1)

                event.arguments = []
                self.on_privnotice(conn, event)
                event.arguments = [
                    u"You will have to re-send that,"
                    u"to the bot that transferred the file."
                ]
                self.on_privnotice(conn, event)

        Tester(u"irc.namibsun.net", u"random").start()
        self.assertTrue(os.path.isfile(u"3_test.txt"))

    def test_failed_dcc_resume_detection(self):

        class Tester(DownloadHandler):

            def on_welcome(self, conn, event):
                self.current_pack = XDCCPack(self.server, u"xdcc_servbot", 2)
                self.pack_queue = []
                self.progress = Progress(1)

                with open(u"2_test.txt", u'w') as f:
                    f.write(u"Test")

                self.dcc_resume_requested = True
                self.connection.whois(self.current_pack.get_bot())

        Tester(u"irc.namibsun.net", u"random").start()
        self.assertTrue(os.path.isfile(u"2_test.txt"))
