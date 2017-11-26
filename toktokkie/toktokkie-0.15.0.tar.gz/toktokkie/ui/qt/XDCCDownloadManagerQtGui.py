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
import sys
import time
from typing import Dict
from threading import Thread
from PyQt5.QtCore import pyqtSignal
from xdcc_dl.entities.Progress import Progress
from xdcc_dl.entities.XDCCPack import XDCCPack
from toktokkie.utils.iconizing.Iconizer import Iconizer
from xdcc_dl.pack_searchers.PackSearcher import PackSearcher
from toktokkie.utils.xdcc.XDCCDownloadManager import XDCCDownloadManager
from toktokkie.utils.renaming.schemes.SchemeManager import SchemeManager
from xdcc_dl.xdcc.MultipleServerDownloader import MultipleServerDownloader
from toktokkie.utils.iconizing.procedures.ProcedureManager import \
    ProcedureManager
from toktokkie.ui.qt.pyuic.xdcc_download_manager import \
    Ui_XDCCDownloadManagerWindow
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QTreeWidgetItem, \
    QHeaderView, QPushButton, QMessageBox


class XDCCDownloadManagerQtGui(QMainWindow, Ui_XDCCDownloadManagerWindow):
    """
    Class that defines the functionality of the XDCC Downloader GUI
    """

    progress_updater_signal = \
        pyqtSignal(float, float, int, int, name="progress_updater")
    download_queue_refresh_signal = \
        pyqtSignal(name="download_queue_refresh_signal")
    spinner_updater_signal = \
        pyqtSignal(QPushButton, str, name="spinner_updater")
    show_download_completed_signal = \
        pyqtSignal(dict, name="show_download_completed")

    def __init__(self, parent: QMainWindow = None) -> None:
        """
        Initializes the interactive components of the GUI

        :param parent: The parent QT GUI
        """
        super().__init__(parent)
        self.setupUi(self)

        self.downloading = False
        self.searching = False

        self.search_results = []
        self.download_queue_list = []

        self.directory_browse_button.clicked.connect(self.browse_for_directory)
        self.download_button.clicked.connect(self.start_download)
        self.search_button.clicked.connect(self.start_search)
        self.search_term_edit.returnPressed.connect(self.start_search)
        self.directory_edit.textChanged.connect(self.parse_directory)

        self.progress_updater_signal.connect(self.update_progress)
        self.download_queue_refresh_signal.connect(self.refresh_download_queue)

        # pragma: no cover
        self.spinner_updater_signal.connect(lambda x, y: x.setText(y))
        self.show_download_completed_signal.connect(
            self.show_download_completed_message_box)

        self.add_to_queue_button.clicked.connect(self.add_to_queue)
        self.remove_from_queue_button.clicked.connect(self.remove_from_queue)

        self.move_up_button.clicked.connect(
            lambda x: self.move_queue_item(up=True))  # pragma: no cover
        self.move_down_button.clicked.connect(
            lambda x: self.move_queue_item(down=True))  # pragma: no cover

        self.show_name_edit.textChanged.connect(self.refresh_download_queue)
        self.season_spin_box.valueChanged.connect(self.refresh_download_queue)
        self.episode_spin_box.valueChanged.connect(self.refresh_download_queue)
        self.auto_rename_check.stateChanged.connect(
            self.refresh_download_queue)

        for scheme in SchemeManager.get_scheme_names():
            self.renaming_scheme_combo_box.addItem(scheme)
        # pragma: no cover
        for procedure in ProcedureManager.get_procedure_names():
            self.iconizing_method_combo_box.addItem(procedure)
        for pack_searcher in ["All"] + \
                PackSearcher.get_available_pack_searchers():
            self.search_engine_combo_box.addItem(pack_searcher)

        self.search_result_list.header().setSectionResizeMode(
            4, QHeaderView.Stretch
        )

        self.directory_edit.setText(os.getcwd())

    def browse_for_directory(self) -> None:  # pragma: no cover
        """
        Lets the user browse for a local directory path

        :return: None
        """
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
        directory = QFileDialog.getExistingDirectory(self, "Browse")
        if directory:
            self.directory_edit.setText(directory)

    def start_search(self) -> None:
        """
        Starts the search using the selected Search engine(s)

        :return: None
        """

        if self.searching:
            return

        def search():

            self.searching = True
            self.start_spinner("search")

            search_term = self.search_term_edit.text()
            search_engine = self.search_engine_combo_box.currentText()

            if search_engine == "All":
                self.search_results = PackSearcher(
                    PackSearcher.get_available_pack_searchers()
                ).search(search_term)
            else:
                self.search_results = \
                    PackSearcher([search_engine]).search(search_term)

            self.search_result_list.clear()
            for i, result in enumerate(self.search_results):
                self.search_result_list.addTopLevelItem(QTreeWidgetItem([
                    str(i),
                    result.get_bot(),
                    str(result.get_packnumber()),
                    str(result.get_size()),
                    result.get_filename()
                ]))
            self.searching = False

        Thread(target=search).start()

    def start_download(self) -> None:
        """
        Starts the download of each item in the download queue

        :return: None
        """
        if self.downloading or len(self.download_queue_list) == 0:
            return

        self.downloading = True
        self.start_spinner("download")

        destination_directory, season_directory = \
            XDCCDownloadManager.prepare_directory(self.directory_edit.text(),
                                                  self.show_name_edit.text(),
                                                  self.season_spin_box.value())

        # noinspection PyShadowingNames
        progress = Progress(
            len(self.download_queue_list),
            callback=lambda a, b, single_progres, d, e, total_progres,
            current_speed, avg_speed:
            self.progress_updater_signal.emit(single_progres, total_progres,
                                              current_speed, avg_speed))

        packs = list(self.download_queue_list)

        for i, pack in enumerate(packs):
            pack.set_directory(season_directory)

            if self.auto_rename_check.checkState():
                name = "xdcc_dl_" + str(i).zfill(int(len(packs) / 10) + 1)
                pack.set_filename(name, override=True)

        def handle_download() -> None:

            results = \
                MultipleServerDownloader("random").download(packs, progress)

            if self.auto_rename_check.checkState():

                scheme = \
                    SchemeManager.get_scheme_from_scheme_name(
                        self.renaming_scheme_combo_box.currentText()
                    )

                XDCCDownloadManager.auto_rename(
                    scheme,
                    self.episode_spin_box.value(),
                    packs
                )

            if self.iconize_check.checkState():

                iconization_method = \
                    self.iconizing_method_combo_box.currentText()
                if iconization_method != "":  # pragma: no cover
                    Iconizer().iconize_directory(destination_directory)

            self.show_download_completed_signal.emit(results)
            self.downloading = False
            self.download_queue_list = []

            self.directory_edit.textChanged.emit("")
            self.download_queue_refresh_signal.emit()
            self.progress_updater_signal.emit(0.0, 0.0, 0, 0)

        Thread(target=handle_download).start()

    def parse_directory(self) -> None:
        """
        Parses the currently entered directory, checks if it contains
        a .meta directory.
        Fills show name, episode and season according to info found.
        Search Term = show name

        :return: None
        """
        season, episode = \
            XDCCDownloadManager.get_max_season_and_episode_number(
                self.directory_edit.text()
            )
        episode += 1

        self.episode_spin_box.setValue(episode)
        self.episode_spin_box.setMinimum(episode)
        self.season_spin_box.setValue(season)

        name = os.path.basename(self.directory_edit.text())
        self.search_term_edit.setText(name)
        self.show_name_edit.setText(name)

    def refresh_download_queue(self) -> None:
        """
        Refreshes the download queue with the current values
        in the download queue list

        :return: None
        """

        if self.auto_rename_check.checkState():

            naming_scheme = SchemeManager.get_scheme_from_scheme_name(
                self.renaming_scheme_combo_box.currentText()
            )

            episodes = XDCCDownloadManager.get_preliminary_renaming_results(
                naming_scheme,
                self.episode_spin_box.value(),
                self.download_queue_list,
                self.season_spin_box.value(),
                self.show_name_edit.text()
            )

            self.download_queue.clear()
            for pack in episodes:
                self.download_queue.addItem(pack)

        else:
            self.download_queue.clear()
            for pack in self.download_queue_list:
                self.download_queue.addItem(pack.get_filename())

    def add_to_queue(self) -> None:
        """
        Add the currently selected items in the search result
        list to the download queue

        :return: None
        """
        for index, row in enumerate(self.search_result_list.selectedIndexes()):
            if index % 5 != 0:
                continue

            self.download_queue_list.append(self.search_results[row.row()])

        self.refresh_download_queue()
        self.search_result_list.clearSelection()

    def remove_from_queue(self) -> None:
        """
        Removes all selected elements from the Download Queue

        :return: None
        """
        rows_to_pop = []
        for row in self.download_queue.selectedIndexes():
            rows_to_pop.append(row.row())

        for row in reversed(sorted(rows_to_pop)):
            self.download_queue_list.pop(row)

        self.refresh_download_queue()

    def move_queue_item(self, up: bool = False, down: bool = False) -> None:
        """
        Moves items on the queue up or down

        :param up:   Pushes the selected elements up
        :param down: Pushes the selected elements down
        :return:     None
        """

        size_check = (lambda x: x > 0) if up and not down else (
            lambda x: x < len(self.download_queue_list) - 1)
        index_change = (lambda x: x - 1) if up and not down else (
            lambda x: x + 1)

        indexes = self.download_queue.selectedIndexes() if up and not down \
            else reversed(self.download_queue.selectedIndexes())

        for row in indexes:

            index = row.row()
            if size_check(index):
                self.download_queue_list.insert(
                    index_change(index),
                    self.download_queue_list.pop(index)
                )

        self.refresh_download_queue()

    def update_progress(self, single_progress: float, total_progress: float,
                        current_speed: int, average_speed: int) -> None:
        """
        Updates the progress bars and speed displays

        :param single_progress: The progress of the current file
        :param total_progress:  The total progress
        :param current_speed:   The current download speed
        :param average_speed:   The average download speed
        :return:                None
        """
        self.single_progress_bar.setValue(single_progress)
        self.total_progress_bar.setValue(total_progress)
        self.current_speed_number.display(int(current_speed / 1000))
        self.average_speed_number.display(int(average_speed / 1000))

    def start_spinner(self, spinner_type: str) -> None:
        """
        Starts a spinner animation while either searching or downloading

        :param spinner_type: The type of spinner
                             (a string that's either 'download' or 'search')
        :return:             None
        """

        search = spinner_type == "search"
        download = spinner_type == "download"

        def spin():

            while (self.searching and search) or \
                    (self.downloading and download):

                if self.searching and search:
                    new_text = \
                        "Searching" + \
                        (self.search_button.text().count(".") % 3 + 1) * "."
                    self.spinner_updater_signal.emit(
                        self.search_button, new_text
                    )

                if self.downloading and download:
                    new_text = \
                        "Downloading" + \
                        (self.download_button.text().count(".") % 3 + 1) * "."
                    self.spinner_updater_signal.emit(
                        self.download_button, new_text
                    )

                time.sleep(0.3)

            if search and not self.searching:
                self.spinner_updater_signal.emit(
                    self.search_button, "Search"
                )
            if download and not self.downloading:
                self.spinner_updater_signal.emit(
                    self.download_button, "Download"
                )

        Thread(target=spin).start()

    # noinspection PyMethodMayBeStatic
    def generate_message(self, icon_type: object, window_title: str,
                         text: str) -> QMessageBox:
        """
        Generates a message dialog.

        :param icon_type:    The type of icon to display
        :param window_title: The title of the dialog box window
        :param text:         The text to display
        """
        msg = QMessageBox()
        msg.setIcon(icon_type)
        msg.setWindowTitle(window_title)
        msg.setText(text)
        msg.setStandardButtons(QMessageBox.Ok)
        return msg

    def show_download_completed_message_box(self, packs: Dict[XDCCPack, str]) \
            -> None:
        """
        Shows a dialog box that indicates that the download has completed

        :param packs: the packs that were downloaded, and their results,
                      as output by the Downloader
        :return:      None
        """
        message = self.generate_message(
            QMessageBox.Information, "Download Complete",
            "The following packs were downloaded:"
        )

        details = ""
        for pack in packs:
            details += pack.get_filename() + ": " + packs[pack] + "\n"
        message.setDetailedText(details.rstrip().lstrip())

        # pragma: no cover
        if not sys.argv == [sys.argv[0], "-platform", "minimal"]:
            message.exec_()

    def closeEvent(self, event: object) -> None:
        """
        Clean up variables that could keep threads from terminating

        :return: None
        """
        self.downloading = False
        self.searching = False
