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
import shutil
import unittest
from toktokkie.utils.xdcc.updating.JsonHandler import JsonHandler
from toktokkie.ui.urwid.XDCCUpdateConfiguratorUrwidTui import \
    XDCCUpdateConfiguratorUrwidTui


class LoopDummy(object):
    def draw_screen(self):
        pass


# noinspection PyTypeChecker
class UnitTests(unittest.TestCase):

    def setUp(self):
        self.tui = XDCCUpdateConfiguratorUrwidTui()
        self.tui.loop = LoopDummy()
        shutil.copytree(os.path.join(
            u"toktokkie", u"tests", u"resources", u"json"), u"json_test")

    def tearDown(self):
        shutil.rmtree(u"json_test")
        self.tui.quit()

    def test_loading_json_file(self):
        self.tui.json_file_location.set_edit_text(
            os.path.join(u"json_test", u"updater.json")
        )
        self.tui.load_json_file(None)

        self.assertEqual(len(self.tui.middle_body), 2)
        self.assertLess(2, len(self.tui.list_walker))

    def test_loading_invalid_json_file(self):
        self.tui.json_file_location.set_edit_text(
            os.path.join(u"json_test", u"invalid-updater.json")
        )
        self.tui.load_json_file(None)

        self.assertEqual(len(self.tui.middle_body), 0)
        self.assertEqual(len(self.tui.list_walker), 3)

    def test_loading_no_file(self):
        self.tui.load_json_file(None)

        self.assertEqual(len(self.tui.middle_body), 0)
        self.assertEqual(len(self.tui.list_walker), 3)

    def test_loading_non_existant_file(self):
        self.tui.json_file_location.set_edit_text(os.path.join(
            u"json_test", u"thisfiledoesnotexist.json"
        ))
        self.tui.load_json_file(None)

        self.assertEqual(len(self.tui.middle_body), 0)
        self.assertEqual(len(self.tui.list_walker), 3)

    def test_adding_series(self):
        self.tui.generate_new_series(None)
        self.assertEqual(len(self.tui.json_handler.get_series()), 1)

        self.assertEqual(
            self.tui.search_name_edit.get_edit_text(),
            u"New Series"
        )
        self.tui.search_name_edit.set_edit_text(u"BlaBla")
        self.assertNotEqual(
            self.tui.search_name_edit.get_edit_text(),
            u"New Series"
        )

        self.tui.generate_new_series(None)
        self.assertEqual(len(self.tui.json_handler.get_series()), 2)
        self.assertEqual(
            self.tui.search_name_edit.get_edit_text(),
            u"New Series"
        )

    def test_removing_series(self):
        self.assertEqual(len(self.tui.json_handler.get_series()), 0)
        self.tui.delete_selected_series(None)
        self.assertEqual(len(self.tui.json_handler.get_series()), 0)

        self.tui.generate_new_series(None)

        self.assertEqual(len(self.tui.json_handler.get_series()), 1)
        self.tui.delete_selected_series(None)
        self.assertEqual(len(self.tui.json_handler.get_series()), 0)

    def test_removing_specific_series(self):
        self.test_loading_json_file()

        series = self.tui.json_handler.get_series()[1]
        self.tui.middle_body[1].set_state(True)
        self.tui.delete_selected_series(None)

        self.assertEqual(len(self.tui.json_handler.get_series()), 1)
        self.assertFalse(self.tui.json_handler.get_series()[0].equals(series))

    def test_saving_unedited_json_file(self):
        self.test_loading_json_file()

        os.remove(os.path.join(u"json_test", u"updater.json"))
        self.tui.save_json_file(None)
        self.assertTrue(os.path.isfile(
            os.path.join(u"json_test", u"updater.json"))
        )

        handler = JsonHandler(os.path.join(u"json_test", u"updater.json"))

        self.assertTrue(handler.get_series()[0].equals(
            self.tui.json_handler.get_series()[0]))
        self.assertTrue(handler.get_series()[1].equals(
            self.tui.json_handler.get_series()[1]))
        self.assertEqual(
            len(handler.get_series()),
            len(self.tui.json_handler.get_series())
        )

    def test_saving_edited_json_file(self):
        self.test_removing_specific_series()
        self.tui.save_json_file(None)

        handler = JsonHandler(os.path.join(u"json_test", u"updater.json"))

        self.assertTrue(handler.get_series()[0].equals(
            self.tui.json_handler.get_series()[0])
        )
        self.assertEqual(
            len(handler.get_series()),
            len(self.tui.json_handler.get_series())
        )

    def test_saving_newly_generated_config(self):
        self.tui.json_file_location.set_edit_text(
            os.path.join(u"json_test", u"generated.json"))
        self.tui.generate_new_series(None)
        self.tui.generate_new_series(None)
        self.tui.generate_new_series(None)
        self.tui.save_json_file(None)

        self.assertTrue(os.path.isfile(os.path.join(
            u"json_test", u"generated.json"))
        )
        self.assertEqual(len(JsonHandler(os.path.join(
            u"json_test", u"generated.json")).get_series()), 3)

    def test_saving_to_empty_string_file_path(self):
        self.tui.generate_new_series(None)
        self.tui.generate_new_series(None)
        self.tui.generate_new_series(None)
        self.tui.save_json_file(None)

        self.assertFalse(os.path.isfile(
            os.path.join(u"json_test", u"generated.json")
        ))
        self.assertEqual(len(self.tui.list_walker), 3)

    def test_saving_to_directory(self):
        self.tui.json_file_location.set_edit_text(u"json_test")
        self.tui.generate_new_series(None)
        self.tui.save_json_file(None)

        self.assertFalse(os.path.isfile(u"json_test"))
        self.assertTrue(os.path.isdir(u"json_test"))
        self.assertEqual(len(self.tui.list_walker), 3)

    def test_modifying_information(self):
        self.tui.generate_new_series(None)
        self.tui.search_name_edit.set_edit_text(u"Modified")
        self.tui.bot_edit.set_edit_text(u"TheBot")
        self.tui.confirm_series_information(None)

        self.assertEqual(
            self.tui.json_handler.get_series()[0].get_search_name(),
            u"Modified"
        )
        self.assertEqual(
            self.tui.json_handler.get_series()[0].get_bot_preference(),
            u"TheBot"
        )
