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
import os
import time
import urwid
import shutil
import unittest
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.XDCCPack import IrcServer
from toktokkie.utils.iconizing.Iconizer import Iconizer
from toktokkie.utils.iconizing.procedures.GenericProcedure import \
    GenericProcedure
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from toktokkie.ui.urwid.XDCCDownloadManagerUrwidTui import \
    XDCCDownloadManagerUrwidTui


class LoopDummy(object):
    def draw_screen(self):
        pass


# noinspection PyTypeChecker
class UnitTests(unittest.TestCase):

    def setUp(self):
        self.tui = XDCCDownloadManagerUrwidTui()
        self.tui.loop = LoopDummy()
        shutil.copytree(
            os.path.join(u"toktokkie", u"tests", u"resources", u"directories"),
            u"temp_testing"
        )

        self.namibsun_packs = [
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 1),
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 2),
            XDCCPack(IrcServer(u"irc.namibsun.net"), u"xdcc_servbot", 3)
        ]

    def tearDown(self):
        Iconizer().reverse_iconization(u"temp_testing")
        shutil.rmtree(u"temp_testing")
        self.tui.quit()

    def test_searching(self):
        self.tui.search_term_edit.set_edit_text(u"1_test.txt")

        for engine in self.tui.search_engines:
            if engine.get_label() == u"namibsun":
                engine.set_state(True)

        self.tui.start_search(None)

        while self.tui.searching:
            pass

        self.assertEqual(len(self.tui.search_results), 1)
        self.assertEqual(len(self.tui.search_result_checks), 1)

    def test_adding_and_removing_search_results_to_queue(self):

        self.tui.search_results = self.namibsun_packs
        self.tui.update_layout()

        self.assertEqual(len(self.tui.search_results), 3)
        self.assertEqual(len(self.tui.search_result_checks), 3)

        self.tui.search_result_checks[0].set_state(True)
        self.tui.search_result_checks[2].set_state(True)

        self.tui.add_search_result_to_queue(None)

        self.assertEqual(len(self.tui.search_results), 3)
        self.assertEqual(len(self.tui.search_result_checks), 3)
        self.assertEqual(len(self.tui.download_queue), 2)
        self.assertEqual(len(self.tui.download_queue_checks), 2)
        self.assertEqual(self.tui.download_queue[0], self.namibsun_packs[0])
        self.assertEqual(self.tui.download_queue[1], self.namibsun_packs[2])

        self.tui.download_queue_checks[0].set_state(True)

        self.tui.remove_items_from_queue(None)
        self.assertEqual(len(self.tui.download_queue), 1)
        self.assertEqual(len(self.tui.download_queue_checks), 1)
        self.assertEqual(self.tui.download_queue[0], self.namibsun_packs[2])

    def test_parsing_directory(self):
        self.tui.target_directory_edit.set_edit_text(
            os.path.join(u"temp_testing", u"Game of Thrones"))
        self.assertEqual(self.tui.series_name_edit.get_edit_text(),
                         u"Game of Thrones")
        self.assertEqual(self.tui.season_number_edit.get_edit_text(), u"2")
        self.assertEqual(self.tui.episode_number_edit.get_edit_text(), u"11")

    def test_downloading_with_iconization_and_renaming(self):
        self.test_parsing_directory()
        self.tui.download_queue = self.namibsun_packs
        self.tui.update_layout()

        self.tui.start_download(None)

        while self.tui.downloading:
            pass

        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E11 - Episode 11.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E12 - Episode 12.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E13 - Episode 13.txt")))
        procedure = ProcedureManager.get_applicable_procedure()

        if procedure != GenericProcedure:
            self.assertNotEqual(procedure.get_icon_file(os.path.join(
                u"temp_testing", u"Game of Thrones")), None)

    def test_downloading_without_iconizing_and_renaming(self):
        self.test_parsing_directory()
        self.tui.download_queue = self.namibsun_packs
        self.tui.update_layout()

        self.tui.iconize_check.set_state(False)
        self.tui.rename_check.set_state(False)

        self.tui.start_download(None)

        while self.tui.downloading:
            pass

        self.assertFalse(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E11 - Episode 11.txt")))
        self.assertFalse(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E12 - Episode 12.txt")))
        self.assertFalse(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E13 - Episode 13.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2", u"1_test.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2", u"2_test.txt")))
        self.assertTrue(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2", u"3_test.txt")))

        procedure = ProcedureManager.get_applicable_procedure()

        if procedure != GenericProcedure:
            self.assertEqual(procedure.get_icon_file(os.path.join(
                u"temp_testing", u"Game of Thrones")), None)

    def test_search_while_searching(self):

        self.tui.search_term_edit.set_edit_text(u"1_test.txt")
        self.tui.start_search(None)

        time.sleep(1)
        self.tui.search_term_edit.set_edit_text(u"2_test.txt")
        self.tui.start_search(None)

        while self.tui.searching:
            pass

        self.assertEqual(len(self.tui.search_results), 1)
        self.assertEqual(
            self.tui.search_results[0].get_filename(),
            u"1_test.txt"
        )

    def test_download_while_downloading(self):
        self.test_parsing_directory()
        self.test_adding_and_removing_search_results_to_queue()
        self.tui.downloading = True
        self.tui.start_download(None)
        self.assertFalse(os.path.isfile(
            os.path.join(u"temp_testing", u"Game of Thrones", u"Season 2",
                         u"Game of Thrones - S02E11 - Episode 11.txt")))

    def test_download_with_invalid_input(self):
        self.test_parsing_directory()
        self.test_adding_and_removing_search_results_to_queue()
        self.tui.episode_number_edit.set_edit_text(u"Not A Number")
        self.tui.start_download(None)
        self.assertFalse(os.path.isfile(os.path.join(
            u"temp_testing", u"Game of Thrones", u"Season 2",
            u"Game of Thrones - S02E11 - Episode 11.txt")))

    def test_download_complete_message(self):

        results = {}
        for pack in self.namibsun_packs:
            results[pack] = u"OK"

        self.tui.show_download_complete_message(results)
        self.assertEqual(5, len(self.tui.list_walker))

        self.tui.update_layout()
        self.assertEqual(5, len(self.tui.list_walker))

        urwid.emit_signal(self.tui.list_walker[4], u'click')

        while len(self.tui.list_walker) == 5:
            pass

        self.assertLess(5, len(self.tui.list_walker))
