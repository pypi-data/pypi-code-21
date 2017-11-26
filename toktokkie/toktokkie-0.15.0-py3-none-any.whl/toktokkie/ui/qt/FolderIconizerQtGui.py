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
import sys
import time
from threading import Thread
from PyQt5.QtCore import pyqtSignal
from toktokkie.utils.iconizing.Iconizer import Iconizer
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from toktokkie.ui.qt.pyuic.iconizer import Ui_FolderIconizerWindow


class FolderIconizerQtGui(QMainWindow, Ui_FolderIconizerWindow):
    """
    Class that defines the functionality of the Folder Iconizer GUI
    """

    spinner_update_signal = pyqtSignal(str, name="spinner_update")

    def __init__(self, parent: QMainWindow = None) -> None:
        """
        Initializes the interactive components of the GUI

        :param parent: The parent QT GUI
        """
        super().__init__(parent)
        self.setupUi(self)

        self.iconizer = Iconizer()
        self.iconizing = False

        self.browse_directory_button.clicked.connect(self.browse_for_directory)
        self.start_button.clicked.connect(self.start_iconizing)

        self.spinner_update_signal.connect(self.update_spinner)

    def browse_for_directory(self) -> None:  # pragma: no cover
        """
        Lets the user browse for a local directory path

        :return: None
        """
        # noinspection PyCallByClass,PyTypeChecker, PyArgumentList
        directory = QFileDialog.getExistingDirectory(self, "Browse")
        if directory:
            self.directory_path_edit.setText(directory)

    def start_iconizing(self) -> None:
        """
        Starts the iconizing process for the specified directory

        :return: None
        """
        self.iconizing = True
        self.start_spinner()
        if self.recursive_check.checkState():
            self.iconizer.recursive_iconize(self.directory_path_edit.text())
        else:
            self.iconizer.iconize_directory(self.directory_path_edit.text())
        self.iconizing = False

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("Complete")
        msg.setText("The iconization has completed")
        msg.setStandardButtons(QMessageBox.Ok)

        # pragma: no cover
        if not sys.argv == [sys.argv[0], "-platform", "minimal"]:
            msg.exec_()

    def start_spinner(self) -> None:
        """
        Starts a little animation on the Start Button to indicate
        that the iconizer is running

        :return: None
        """
        def spinner():
            while self.iconizing:
                new_text = "Iconizing" + \
                           (self.start_button.text().count(".") % 3 + 1) * "."
                self.spinner_update_signal.emit(new_text)
                time.sleep(0.3)

                self.spinner_update_signal.emit("Start")

        Thread(target=spinner).start()

    def update_spinner(self, text: str) -> None:
        """
        Updates the text on the Start Button

        :param text: The text to be displayed on the Start button
        :return:     None
        """
        self.start_button.setText(text)

    def closeEvent(self, event: object) -> None:
        """
        Clean up variables that could keep threads from terminating

        :return: None
        """
        self.iconizing = False
