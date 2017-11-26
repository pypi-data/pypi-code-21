"""
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
import os
import urwid
from xdcc_dl.pack_searchers.PackSearcher import PackSearcher
from toktokkie.utils.xdcc.updating.objects.Series import Series
from toktokkie.utils.xdcc.updating.JsonHandler import JsonHandler
from toktokkie.utils.xdcc.updating.AutoSearcher import AutoSearcher
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager


class XDCCUpdateConfiguratorUrwidTui(object):
    """
    Urwid TUI for the XDCC Download Manager functionality
    """

    def __init__(self) -> None:
        """
        Initializes the TUI's various widgets
        """
        self.upper_body = []
        self.middle_body = []
        self.lower_body = []

        self.loop = None
        self.top = None
        self.list_walker = None

        self.json_handler = JsonHandler()
        self.selected_series = None

        self.title_text = urwid.Text("XDCC Update Configurator")

        self.json_file_location = urwid.Edit(caption="JSON File: ")
        self.open_button = urwid.Button("Open JSON file")
        self.save_button = urwid.Button("Save JSON file")

        self.new_series_button = urwid.Button("New Series")
        self.delete_series_button = urwid.Button("Delete selected Series")

        self.configuration_header = urwid.Text("Series Configuration")
        self.series_directory_edit = urwid.Edit("Directory:   ")
        self.search_name_edit = urwid.Edit("Search Name: ")
        self.bot_edit = urwid.Edit("Bot:         ")
        self.season_edit = urwid.IntEdit("Season:      ")

        self.quality_selector_title = urwid.Text("Quality:")
        self.quality_selectors = []
        for quality in ["480p", "720p", "1080p"]:
            urwid.RadioButton(self.quality_selectors, quality)

        self.search_engine_title = urwid.Text("Search Engine: ")
        self.search_engines = []
        for engine in PackSearcher.get_available_pack_searchers():
            urwid.RadioButton(self.search_engines, engine)

        self.naming_scheme_title = urwid.Text("Naming Schemes:")
        self.naming_schemes = []
        for scheme in SchemeManager.get_scheme_names():  # pragma: no cover
            urwid.RadioButton(self.naming_schemes, scheme)

        self.naming_pattern_title = urwid.Text("Naming Pattern")
        self.naming_patterns = []
        for pattern in AutoSearcher.get_available_patterns():
            urwid.RadioButton(self.naming_patterns, pattern)

        self.confirm_button = urwid.Button("Confirm Changes")

        urwid.connect_signal(self.open_button, 'click', self.load_json_file)
        urwid.connect_signal(self.save_button, 'click', self.save_json_file)
        urwid.connect_signal(
            self.new_series_button, 'click', self.generate_new_series)
        urwid.connect_signal(
            self.delete_series_button, 'click', self.delete_selected_series)
        urwid.connect_signal(
            self.confirm_button, 'click', self.confirm_series_information)

        self.lay_out()

    def lay_out(self) -> None:
        """
        Handles the layout of the TUI elements

        :return: None
        """
        div = urwid.Divider()

        open_button = urwid.AttrMap(
            self.open_button, None, focus_map='reversed')
        save_button = urwid.AttrMap(
            self.save_button, None, focus_map='reversed')
        new_series_button = urwid.AttrMap(
            self.new_series_button, None, focus_map='reversed')
        delete_series_button = urwid.AttrMap(
            self.delete_series_button, None, focus_map='reversed')
        confirm_button = urwid.AttrMap(
            self.confirm_button, None, focus_map='reversed')

        self.upper_body = [
            self.title_text, div, self.json_file_location,
            open_button, save_button, div
        ]
        self.lower_body = [
            new_series_button, delete_series_button, div,
            self.configuration_header, self.series_directory_edit,
            self.search_name_edit, self.bot_edit, self.season_edit
        ]
        self.lower_body += [self.quality_selector_title] + \
            self.quality_selectors
        self.lower_body += [self.search_engine_title] + self.search_engines
        self.lower_body += [self.naming_scheme_title] + self.naming_schemes
        self.lower_body += [self.naming_pattern_title] + self.naming_patterns
        self.lower_body += [confirm_button]

        self.list_walker = \
            urwid.SimpleFocusListWalker(self.upper_body + self.lower_body)
        self.top = urwid.Overlay(
            urwid.Padding(urwid.ListBox(self.list_walker), left=2, right=2),
            urwid.SolidFill(u'\N{MEDIUM SHADE}'),
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 70),
            min_width=20, min_height=10
        )

    def start(self) -> None:  # pragma: no cover
        """
        Starts the TUI

        :return: None
        """
        self.loop = \
            urwid.MainLoop(self.top, palette=[('reversed', 'standout', '')])
        self.loop.run()

    # noinspection PyUnusedLocal
    def refresh_ui(self, button: urwid.Button = None) -> None:
        """
        Refreshes the UI elements

        :param button: The button that called this method,
                       if it was called by a button
        :return:       None
        """
        self.selected_series = None if len(self.json_handler.get_series()) < 1\
            else self.json_handler.get_series()[0]
        self.middle_body = []

        for series in self.json_handler.get_series():
            urwid.RadioButton(self.middle_body, series.get_search_name())
        for i, radio in enumerate(self.middle_body):
            urwid.connect_signal(radio, 'change', self.select_series)
            radio.series = self.json_handler.get_series()[i]

        self.list_walker[:] = \
            self.upper_body + self.middle_body + self.lower_body
        self.loop.draw_screen()

    def select_series(self, radio_button: urwid.RadioButton, state: bool) \
            -> None:
        """
        Handles selecting a series. It auto-populates the entries below
        the list of series.

        :param radio_button: The radio button representing the series
        :param state:        The state of that radio button
        :return:             None
        """
        if not state:
            return

        self.selected_series = radio_button.series
        self.series_directory_edit.set_edit_text(
            self.selected_series.get_destination_directory())
        self.search_name_edit.set_edit_text(
            self.selected_series.get_search_name())
        self.season_edit.set_edit_text(str(self.selected_series.get_season()))
        self.bot_edit.set_edit_text(self.selected_series.get_bot_preference())

        for quality in self.quality_selectors:
            if quality.get_label() == \
                    self.selected_series.get_quality_identifier():
                quality.set_state(True)
        for engine in self.search_engines:
            if engine.get_label() == \
                    self.selected_series.get_search_engines()[0]:
                engine.set_state(True)
        for scheme in self.naming_schemes:
            # pragma: no cover
            if scheme.get_label() == \
                    self.selected_series.get_naming_scheme():
                scheme.set_state(True)
        for pattern in self.naming_patterns:
            if pattern.get_label() == \
                    self.selected_series.get_search_pattern():
                pattern.set_state(True)

        self.loop.draw_screen()

    def show_message(self, message: str) -> None:
        """
        Shows a message dialog

        :param message: The message to display
        :return:        None
        """
        confirm_button = urwid.Button("OK")
        urwid.connect_signal(confirm_button, 'click', self.refresh_ui)
        self.list_walker[:] = \
            [urwid.Text(message), urwid.Divider(), confirm_button]

    # noinspection PyUnusedLocal
    def load_json_file(self, button: urwid.Button) -> None:
        """
        Tries to load the currently entered json file.
        If it fails, the user is informed via a message dialog

        :param button: The button that called this method
        :return:       None
        """
        filepath = self.json_file_location.get_edit_text()
        if not os.path.isfile(filepath):
            self.show_message(
                "The entered file path is not valid: \n\n" + filepath
            )
            return

        try:
            self.json_handler = JsonHandler(filepath)
            self.refresh_ui()
        except ValueError:
            self.show_message("The specified file is either not a valid JSON"
                              "file or not in the proper format.")

    # noinspection PyUnusedLocal
    def save_json_file(self, button: urwid.Button) -> None:
        """
        Saves the current state of the JSON handler
        to the currently entered file

        :param button: The button that called this method
        :return:       None
        """
        filepath = self.json_file_location.get_edit_text()
        if os.path.isdir(filepath):
            self.show_message("The specified path is a directory")
        elif filepath == "":
            self.show_message("Please enter a file path for the JSON file")
        else:
            self.json_handler.store_json(filepath)
            self.show_message("JSON file saved successfully")

    # noinspection PyUnusedLocal
    def generate_new_series(self, button: urwid.Button) -> None:
        """
        Generates a new Series in the JSON Handler

        :param button: The button that called this method
        :return:       None
        """
        self.json_handler.add_series(
            Series(
                os.getcwd(), "New Series", "480p", "Bot", 1, ["nibl"],
                "Plex (TVDB)", "horriblesubs"
            )
        )
        self.refresh_ui()

        if self.middle_body[len(self.middle_body) - 1].get_state():
            self.select_series(
                self.middle_body[len(self.middle_body) - 1],
                True
            )
        else:
            self.middle_body[len(self.middle_body) - 1].set_state(True)

    # noinspection PyUnusedLocal
    def delete_selected_series(self, button: urwid.Button) -> None:
        """
        Deletes the currently selected series

        :param button: The button that called this method
        :return:       None
        """
        self.json_handler.remove_series(self.selected_series)
        self.refresh_ui()

    # noinspection PyUnusedLocal
    def confirm_series_information(self, button: urwid.Button) -> None:
        """
        Stores the currently entered information in the JSON handler
        (in-memory)

        :param button: The button that called this method
        :return:       None
        """
        self.json_handler.remove_series(self.selected_series)
        self.json_handler.add_series(
            Series(self.series_directory_edit.get_edit_text(),
                   self.search_name_edit.get_edit_text(),
                   list(filter(
                       lambda x: x.get_state(),
                       self.quality_selectors
                   ))[0].get_label(),
                   self.bot_edit.get_edit_text(),
                   int(self.season_edit.get_edit_text()),
                   [list(filter(
                       lambda x: x.get_state(),
                       self.search_engines
                   ))[0].get_label()],
                   list(filter(
                       lambda x: x.get_state(),
                       self.naming_schemes
                   ))[0].get_label(),
                   list(filter(
                       lambda x: x.get_state(),
                       self.naming_patterns
                   ))[0].get_label(),
                   )
        )
        self.refresh_ui()
        self.middle_body[len(self.middle_body) - 1].set_state(True)

    # noinspection PyMethodMayBeStatic
    def quit(self) -> None:
        """
        Cleans up any variables that may cause thread to
        continue executing after the TUI ends

        :return: None
        """
        pass
