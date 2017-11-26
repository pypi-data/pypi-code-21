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
import urwid
from typing import Dict
from toktokkie import version
from xdcc_dl.tui.XDCCDownloaderTui import XDCCDownloaderTui
from toktokkie.ui.urwid.FolderIconizerUrwidTui import FolderIconizerUrwidTui
from toktokkie.ui.urwid.TVSeriesRenamerUrwidTui import TVSeriesRenamerUrwidTui
from toktokkie.ui.urwid.XDCCDownloadManagerUrwidTui import \
    XDCCDownloadManagerUrwidTui
from toktokkie.ui.urwid.XDCCUpdateConfiguratorUrwidTui import \
    XDCCUpdateConfiguratorUrwidTui


class StartScreenUrwidTui(object):
    """
    A Class handling the state of the start screen TUI
    """

    def __init__(self) -> None:
        """
        Initializes the CLI's local variables
        """
        gpl_notice = \
            "Tok Tokkie Media Manager V" + version + "\n"\
            "Copyright (C) 2015,2016 Hermann Krumrey\n\n"\
            "This program comes with ABSOLUTELY NO WARRANTY; "\
            "for details type `show w'.\n"\
            "This is free software, and you are welcome to redistribute it\n"\
            "under certain conditions; type `show c' for details."

        options = {"TV Series Renamer": TVSeriesRenamerUrwidTui,
                   "Folder Iconizer": FolderIconizerUrwidTui,
                   "XDCC Downloader": XDCCDownloaderTui,
                   "XDCC Download Manager": XDCCDownloadManagerUrwidTui,
                   "XDCC Update Configurator": XDCCUpdateConfiguratorUrwidTui}

        self.selected = None

        self.menu = urwid.Padding(
            self.generate_menu(gpl_notice, options), left=2, right=2
        )
        self.top = urwid.Overlay(
            self.menu, urwid.SolidFill(u'\N{MEDIUM SHADE}'),
            align='center', width=('relative', 80),
            valign='middle', height=('relative', 70),
            min_width=20, min_height=10
        )

    def start(self) -> None:  # pragma: no cover
        """
        Starts the TUI

        :return: None
        """
        urwid.MainLoop(self.top, palette=[('reversed', 'standout', '')]).run()
        if self.selected is not None:
            child = self.selected()
            child.start()
            child.quit()

    def generate_menu(self, header: str, options: Dict[str, object]) -> \
            urwid.ListBox:
        """
        Generates the Menu for selecting which module to use

        :param header:  The Title of the menu
        :param options: The available options for the Menu
        :return:        The Menu, which is a urwid ListBox
        """
        body = [urwid.Text(header), urwid.Divider()]
        for option in sorted(options.keys()):
            button = urwid.Button(option)
            urwid.connect_signal(
                button,
                'click',
                self.start_tui,
                user_arg=options[option]
            )
            body.append(urwid.AttrMap(button, None, focus_map='reversed'))
        return urwid.ListBox(urwid.SimpleFocusListWalker(body))

    # pragma: no cover
    # noinspection PyUnusedLocal,PyMethodMayBeStatic
    def start_tui(self, button: urwid.Button, choice: object = None) -> None:
        """
        Starts the selected TUI option when pressing Enter

        :param button: The button that was pressed
        :param choice: The choice associated with that button
        :return:       None
        """
        if choice is not None:
            # noinspection PyCallingNonCallable
            self.selected = choice
            raise urwid.ExitMainLoop()
