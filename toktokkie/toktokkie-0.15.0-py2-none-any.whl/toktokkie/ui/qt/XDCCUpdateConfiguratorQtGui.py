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
import sys
from xdcc_dl.pack_searchers.PackSearcher import PackSearcher
from toktokkie.utils.xdcc.updating.objects.Series import Series
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from toktokkie.utils.xdcc.updating.JsonHandler import JsonHandler
from toktokkie.utils.xdcc.updating.AutoSearcher import AutoSearcher
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager
from toktokkie.ui.qt.pyuic.xdcc_update_configurator import \
    Ui_XDCCUpdateConfiguratorWindow


class XDCCUpdateConfiguratorQtGui(
        QMainWindow, Ui_XDCCUpdateConfiguratorWindow):
    u"""
    Class that defines the functionality of the XDCC Updater GUI
    """

    def __init__(self, parent = None):
        u"""
        Initializes the interactive components of the GUI

        :param parent: The parent QT GUI
        """
        super(XDCCUpdateConfiguratorQtGui, self).__init__(parent)
        self.setupUi(self)

        self.file_loaded = False

        for naming_scheme in SchemeManager.get_scheme_names():
            self.naming_scheme_combo_box.addItem(naming_scheme)
        for pattern in AutoSearcher.get_available_patterns():
            self.pattern_combo_box.addItem(pattern)
        for searcher in PackSearcher.get_available_pack_searchers():
            self.search_engine_combo_box.addItem(searcher)

        self.load_button.clicked.connect(self.browse_for_json_file)
        self.save_button.clicked.connect(self.save_json)
        self.new_button.clicked.connect(self.create_new_series)
        self.confirm_button.clicked.connect(self.store_selected_series)
        self.delete_button.clicked.connect(self.delete_selected_series)
        self.series_list.selectionModel().selectionChanged.connect(
            self.load_selected_series
        )

        self.json_handler = JsonHandler()
        self.series = []

    def browse_for_json_file(self):
        u"""
        Lets the user browse for the JSON file containing
        the updater configuration

        :return: None
        """
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
        selected = QFileDialog.getOpenFileName(self, u"Browse", filter=u"*.json")
        if selected[0]:
            try:
                self.json_handler = JsonHandler(selected[0])
                self.file_loaded = True
                self.populate_series_list()
            except ValueError:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle(u"Invalid JSON")
                msg.setText(u"The specified file is not a valid JSON file.")
                msg.setStandardButtons(QMessageBox.Ok)

                # pragma: no cover
                if not sys.argv == [sys.argv[0], u"-platform", u"minimal"]:
                    msg.exec_()

    def save_json(self):
        u"""
        Saves the JSON file, if it already exists, else it asks the user
        for a place to save it beforehand

        :return: None
        """
        if self.file_loaded:
            self.json_handler.store_json()

            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle(u"Save Successful")
            msg.setText(
                u"The file has been saved to: " +
                self.json_handler.get_json_file_path()
            )
            msg.setStandardButtons(QMessageBox.Ok)

            # pragma: no cover
            if not sys.argv == [sys.argv[0], u"-platform", u"minimal"]:
                msg.exec_()
        else:
            # noinspection PyCallByClass,PyTypeChecker
            destination = QFileDialog.getSaveFileName(
                self, u"Save", os.getcwdu(), filter=u"*.json",
                options=QFileDialog.DontConfirmOverwrite)[0]

            if destination:
                destination_file = destination \
                    if destination.endswith(u".json") \
                    else destination + u".json"
                self.json_handler.store_json(destination_file)
                self.file_loaded = True

    def populate_series_list(self):
        u"""
        Populates the series list with the series loaded from the JSON file

        :return: None
        """
        self.series_list.clear()
        self.series = self.json_handler.get_series()

        for series in self.series:
            self.series_list.addItem(series.get_search_name())

    def load_selected_series(self):
        u"""
        Loads the selected series from the series list

        :return: None
        """
        try:
            selected_series = \
                self.series[self.series_list.selectedIndexes()[0].row()]
        except IndexError:
            return

        self.directory_edit.setText(
            selected_series.get_destination_directory()
        )
        self.search_name_edit.setText(selected_series.get_search_name())

        self.quality_combo_box.setCurrentIndex(
            self.quality_combo_box.findText(
                selected_series.get_quality_identifier())
        )

        self.bot_edit.setText(selected_series.get_bot_preference())
        self.season_spin_box.setValue(selected_series.get_season())
        self.episode_offset_spinbox.setValue(
            selected_series.get_episode_offset()
        )

        self.search_engine_combo_box.setCurrentIndex(
            self.search_engine_combo_box.findText(
                selected_series.get_search_engines()[0])
        )

        self.naming_scheme_combo_box.setCurrentIndex(
            self.naming_scheme_combo_box.findText(
                selected_series.get_naming_scheme())
        )

        self.pattern_combo_box.setCurrentIndex(
            self.pattern_combo_box.findText(
                selected_series.get_search_pattern())
        )

    def store_selected_series(self):
        u"""
        Stores the currently selected series in the json handler

        :return: None
        """
        try:
            prev_series = \
                self.series[self.series_list.selectedIndexes()[0].row()]
        except IndexError:
            return

        series = Series(self.directory_edit.text(),
                        self.search_name_edit.text(),
                        self.quality_combo_box.currentText(),
                        self.bot_edit.text(),
                        self.season_spin_box.value(),
                        [self.search_engine_combo_box.currentText()],
                        self.naming_scheme_combo_box.currentText(),
                        self.pattern_combo_box.currentText(),
                        self.episode_offset_spinbox.value())

        self.json_handler.add_series(series)
        self.json_handler.remove_series(prev_series)
        self.populate_series_list()

    def create_new_series(self):
        u"""
        Creates a new series

        :return: None
        """
        series = Series(
            os.getcwdu(), u"New Series", u"1080p", u"Bot", 1,
            [u"nibl"], u"Plex (TVDB)", u"horriblesubs"
        )
        self.json_handler.add_series(series)

        self.populate_series_list()

    def delete_selected_series(self):
        u"""
        Deletes the selected series

        :return: None
        """
        try:
            selected_series = self.series[
                self.series_list.selectedIndexes()[0].row()
            ]
            self.json_handler.remove_series(selected_series)
            self.populate_series_list()
        except IndexError:
            pass

    def closeEvent(self, event):
        u"""
        Clean up variables that could keep threads from terminating

        :return: None
        """
        pass
