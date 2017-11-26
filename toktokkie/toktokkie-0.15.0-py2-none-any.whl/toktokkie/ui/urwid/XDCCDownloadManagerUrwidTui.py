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
from __future__ import division
from __future__ import absolute_import
import os
import time
import urwid
from typing import Dict
from threading import Thread
from xdcc_dl.entities.XDCCPack import XDCCPack
from xdcc_dl.entities.Progress import Progress
from toktokkie.utils.iconizing.Iconizer import Iconizer
from xdcc_dl.pack_searchers.PackSearcher import PackSearcher
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager
from toktokkie.utils.xdcc.XDCCDownloadManager import XDCCDownloadManager
from xdcc_dl.xdcc.MultipleServerDownloader import MultipleServerDownloader
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from itertools import ifilter


class XDCCDownloadManagerUrwidTui(object):
    u"""
    Urwid TUI for the XDCC Download Manager functionality
    """

    def __init__(self):
        u"""
        Initializes the TUI's various widgets
        """

        self.searching = False
        self.downloading = False
        self.message_dialog_showing = False

        self.upper_body = []
        self.upper_middle_body = []
        self.middle_body = []
        self.lower_middle_body = []
        self.lower_body = []

        self.loop = None
        self.top = None
        self.list_walker = None

        self.title = urwid.Text(u"XDCC Download Manager")
        self.target_directory_edit = urwid.Edit(u"Target Directory:")
        self.target_directory_edit.set_edit_text(os.getcwdu())
        self.series_name_edit = urwid.Edit(u"Series Name:")
        self.season_number_edit = urwid.Edit(u"Season Number:")
        self.episode_number_edit = urwid.Edit(u"Episode Number:")

        self.renaming_schemes = []
        for scheme in SchemeManager.get_scheme_names():
            urwid.RadioButton(self.renaming_schemes, scheme)
        self.rename_check = urwid.CheckBox(u"Auto-rename", state=True)

        self.iconizing_procedures = []

        # pragma: no cover
        for procedure in ProcedureManager.get_procedure_names():
            urwid.RadioButton(self.iconizing_procedures, procedure)
        self.iconize_check = urwid.CheckBox(u"Iconize", state=True)

        self.search_term_edit = urwid.Edit(u"Search Term:")
        self.search_engines = []
        for engine in [u"All"] + PackSearcher.get_available_pack_searchers():
            urwid.RadioButton(self.search_engines, engine)

        self.search_button = urwid.Button(u"Search")

        self.search_results = []
        self.search_result_checks = []

        self.add_search_results_button = urwid.Button(u"Add Selected Packs")

        self.download_queue_label = urwid.Text(u"Download Queue:")
        self.download_queue = []
        self.download_queue_checks = []

        self.remove_queue_items_button = urwid.Button(u"Remove Selected Packs")

        self.download_button = urwid.Button(u"Download")

        self.single_progress_bar = urwid.ProgressBar(u"Single N", u"Single C")
        self.total_progress_bar = urwid.ProgressBar(u"Total N", u"Total N")
        self.current_speed = urwid.Text(u"Current Speed:")
        self.average_speed = urwid.Text(u"Average Speed:")

        self.lay_out()
        self.connect_widgets()

    def lay_out(self):
        u"""
        Handles the layout of the TUI elements

        :return: None
        """
        div = urwid.Divider()

        self.upper_body = [
            self.title, div, self.target_directory_edit, self.series_name_edit,
            self.season_number_edit
        ]
        self.upper_body += [self.episode_number_edit, div] + \
            self.renaming_schemes + [self.rename_check, div]
        self.upper_body += self.iconizing_procedures + \
            [self.iconize_check, div, self.search_term_edit]
        self.upper_body += self.search_engines + [self.search_button, div]

        self.middle_body = [
            self.add_search_results_button, div, self.download_queue_label
        ]

        self.lower_body = [
            self.remove_queue_items_button, div, self.download_button, div,
            self.single_progress_bar, self.total_progress_bar,
            self.current_speed, self.average_speed
        ]

        body = self.upper_body + self.middle_body + self.lower_body

        self.list_walker = urwid.SimpleFocusListWalker(body)
        self.top = urwid.Overlay(
            urwid.Padding(urwid.ListBox(self.list_walker), left=2, right=2),
            urwid.SolidFill(u'\N{MEDIUM SHADE}'),
            align=u'center', width=(u'relative', 80),
            valign=u'middle', height=(u'relative', 70),
            min_width=20, min_height=10
        )

    def update_layout(self):
        u"""
        Updates the layout of the TUI Widgets

        :return: None
        """

        if self.message_dialog_showing:
            return

        self.search_result_checks = []
        for result in self.search_results:
            self.search_result_checks.append(
                urwid.CheckBox(result.get_filename())
            )

        self.download_queue_checks = []
        for item in self.download_queue:
            self.download_queue_checks.append(urwid.CheckBox(
                item.get_request_message(full=True))
            )

        self.upper_middle_body = self.search_result_checks
        self.lower_middle_body = self.download_queue_checks
        body = self.upper_body + self.upper_middle_body + self.middle_body + \
            self.lower_middle_body + self.lower_body

        self.list_walker[:] = body
        self.loop.draw_screen()

    def connect_widgets(self):
        u"""
        Connects the various widgets to their functionality

        :return: None
        """
        urwid.connect_signal(
            self.target_directory_edit, u'change', self.parse_directory)
        urwid.connect_signal(
            self.search_button, u'click', self.start_search)
        urwid.connect_signal(
            self.download_button, u'click', self.start_download)
        urwid.connect_signal(
            self.add_search_results_button, u'click',
            self.add_search_result_to_queue)
        urwid.connect_signal(
            self.remove_queue_items_button, u'click',
            self.remove_items_from_queue)

    def start(self):  # pragma: no cover
        u"""
        Starts the TUI

        :return: None
        """
        self.loop = urwid.MainLoop(
            self.top, palette=[(u'reversed', u'standout', u'')]
        )
        self.loop.run()

    # noinspection PyUnusedLocal
    def parse_directory(self, widget, directory):
        u"""
        Parses the currently entered directory, and fills in the information
        it can gather from that into the relevant UI elements

        :param widget:    The widget that did the method call
        :param directory: The new content of the widget's edit text
        :return:          None
        """
        series_name = os.path.basename(directory)
        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(directory)
        episode += 1

        self.series_name_edit.set_edit_text(series_name)
        self.search_term_edit.set_edit_text(series_name)
        self.episode_number_edit.set_edit_text(unicode(episode))
        self.season_number_edit.set_edit_text(unicode(season))

    # noinspection PyUnusedLocal
    def add_search_result_to_queue(self, button):
        u"""
        Add all currently checked search results to the download queue

        :param button: The add results button
        :return:       None
        """
        for i, result in enumerate(self.search_result_checks):
            if result.get_state():
                self.download_queue.append(self.search_results[i])
            result.set_state(False)
        self.update_layout()

    # noinspection PyUnusedLocal
    def remove_items_from_queue(self, button):
        u"""
        Removes all selected items from the queue

        :param button: The button that called this method
        :return:       None
        """
        pop_indexes = []
        for i, item in enumerate(self.download_queue_checks):
            if item.get_state():
                pop_indexes.append(i)

        for index in reversed(sorted(pop_indexes)):
            self.download_queue.pop(index)
        self.update_layout()

    # noinspection PyUnusedLocal
    def start_search(self, widget):
        u"""
        Starts searching for the XDCC pack specified via the search term
        and search engines to use

        :param widget: The widget that called this method
        :return:       None
        """
        if self.searching or self.downloading:
            return

        self.searching = True
        self.start_spinner(u"search")

        def search():

            search_term = self.search_term_edit.get_edit_text()
            search_engine = list(ifilter(
                lambda x: x.get_state(), self.search_engines)
            )[0].get_label()

            if search_engine == u"All":
                self.search_results = \
                    PackSearcher(PackSearcher.get_available_pack_searchers())\
                    .search(search_term)
            else:
                self.search_results = \
                    PackSearcher([search_engine]).search(search_term)

            self.update_layout()
            self.searching = False

        Thread(target=search).start()

    # noinspection PyUnusedLocal
    def start_download(self, widget):
        u"""
        Starts the XDCC download procedure

        :param widget: The widget that called this method
        :return:       None
        """
        if self.downloading or self.searching:
            return

        try:
            season = int(self.season_number_edit.get_edit_text())
            episode = int(self.episode_number_edit.get_edit_text())
        except ValueError:
            return

        self.downloading = True
        self.start_spinner(u"download")

        destination_directory, season_directory = \
            XDCCDownloadManager.prepare_directory(
                self.target_directory_edit.get_edit_text(),
                self.series_name_edit.get_edit_text(),
                season
            )

        for i, pack in enumerate(self.download_queue):
            pack.set_directory(season_directory)

            if self.rename_check.get_state():
                name = u"xdcc_dl_" + \
                       unicode(i).zfill(int(len(self.download_queue) / 10) + 1)
                pack.set_filename(name, override=True)

        # noinspection PyShadowingNames
        progress = Progress(
            len(self.download_queue),
            callback=lambda a, b, single_progress, d, e, total_progress,
            current_speed, average_speed:
            self.progress_update(
                single_progress, total_progress, current_speed, average_speed)
        )

        def handle_download():

            results = MultipleServerDownloader(u"random").\
                download(self.download_queue, progress)

            if self.rename_check.get_state():
                scheme = SchemeManager.get_scheme_from_scheme_name(
                    list(ifilter(
                        lambda x: x.get_state(),
                        self.renaming_schemes)
                    )[0].get_label())

                XDCCDownloadManager.auto_rename(
                    scheme, episode, self.download_queue
                )

            if self.iconize_check.get_state():
                try:  # pragma: no cover
                    iconization_method = list(ifilter(
                        lambda x: x.get_state(),
                        self.iconizing_procedures
                    ))[0].get_label()
                    Iconizer(iconization_method).iconize_directory(
                        destination_directory
                    )
                except IndexError:  # pragma: no cover
                    pass

            self.downloading = False
            self.progress_update(0.0, 0.0, 0, 0)
            self.current_speed.set_text(u"Current Speed:")
            self.average_speed.set_text(u"Average Speed:")
            self.download_queue = []
            self.parse_directory(
                self.target_directory_edit,
                self.target_directory_edit.get_edit_text()
            )
            self.update_layout()
            self.show_download_complete_message(results)

        Thread(target=handle_download).start()

    def start_spinner(self, spinner_type):
        u"""
        Animates the search and download buttons whenever
        a search or download is running

        :param spinner_type: The type of spinner to use,
                             can be either 'download' or 'search'
        :return:             None
        """

        download = spinner_type == u"download"
        search = spinner_type == u"search"

        def spin_thread():

            while (self.downloading and download) or \
                    (self.searching and search):

                if self.downloading and download:
                    new_text = u"Downloading" + \
                               (self.download_button.get_label().count(u".") % 3
                                + 1) * u"."
                    self.download_button.set_label(new_text)

                if self.searching and search:
                    new_text = u"Searching" + \
                               (self.search_button.get_label().count(u".") % 3
                                + 1) * u"."
                    self.search_button.set_label(new_text)

                self.loop.draw_screen()
                time.sleep(0.3)

            if download:
                self.download_button.set_label(u"Download")
            if search:
                self.search_button.set_label(u"Search")
            self.loop.draw_screen()

        Thread(target=spin_thread).start()

    # noinspection PyUnusedLocal
    def progress_update(self, single_percentage,
                        total_percentage, current_speed,
                        average_speed):
        u"""
        Updates the TUI's progress widgets

        :param single_percentage:  The Single Completion Percentage
        :param total_percentage:   The Total Completion Percentage
        :param current_speed:      The current speed in Byte/s
        :param average_speed:      The average speed in Byte/s
        :return:                   None
        """
        self.single_progress_bar.set_completion(int(single_percentage))
        self.total_progress_bar.set_completion(int(total_percentage))
        self.current_speed.set_text(u"Current Speed: " +
                                    unicode(int(current_speed / 1000)) + u" kB/s")
        self.average_speed.set_text(u"Average Speed: " +
                                    unicode(int(average_speed / 1000)) + u" kB/s")
        self.loop.draw_screen()

    def show_download_complete_message(self, packs):
        u"""
        Shows a message dialog when the download is completed

        :param packs: The download results generated by the downloader
        :return:      None
        """
        def remove_message_box():
            self.message_dialog_showing = False
            self.update_layout()

        self.message_dialog_showing = True

        message = urwid.Text(
            u"Download has completed successfully\nDownloaded Packs:"
        )
        div = urwid.Divider()

        details = u""
        for pack in packs:
            details += pack.get_filename() + u": " + packs[pack] + u"\n"
        details_text = urwid.Text(details.rstrip().lstrip())

        confirm_button = urwid.Button(u"OK")
        urwid.connect_signal(confirm_button, u'click', remove_message_box)
        self.list_walker[:] = [message, div, details_text, div, confirm_button]
        self.loop.draw_screen()

    def quit(self):
        u"""
        Cleans up any variables that may cause thread to continue
        executing after the TUI ends

        :return: None
        """
        self.downloading = False
        self.searching = False
