###########################################################################
# Top30 is Copyright (C) 2016-2017 Kyle Robbertze <krobbertze@gmail.com>
#
# Top30 is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 3 as
# published by the Free Software Foundation.
#
# Top30 is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Top30.  If not, see <http://www.gnu.org/licenses/>.
###########################################################################
"""  
Main UI handlers
"""  
import os
import sys
from PyQt5 import QtCore, QtWidgets, uic

import top30
from top30.top_30_creator import Top30Creator
from top30.clip_list import ClipListModel
from top30.main_window import Ui_MainWindow

class MainWindow(QtWidgets.QMainWindow):
    """
    The main window for the GUI version of top30
    """
    def __init__(self, creator):
        super(MainWindow, self).__init__()
        self.creator = creator
        ui_file = top30.find_file("main_window.ui")
        uic.loadUi(ui_file, self)
        self.init_ui()

    def init_ui(self):
        """ Initialises the UI """
        self.btn_add_clip.clicked.connect(self.on_add_clip_clicked)
        self.btn_move_up.clicked.connect(self.on_move_up_clicked)
        self.btn_move_down.clicked.connect(self.on_move_down_clicked)
        self.btn_delete_clip.clicked.connect(self.on_delete_clip_clicked)
        self.btn_create.clicked.connect(self.on_create_clip_clicked)

        self.act_new.triggered.connect(self.on_new_clicked)
        self.act_exit.triggered.connect(QtWidgets.qApp.quit)
        self.act_create_clip.triggered.connect(self.on_create_clip_clicked)
        self.act_add_clip.triggered.connect(self.on_add_clip_clicked)
        self.act_delete_clip.triggered.connect(self.on_delete_clip_clicked)

        self.load_settings()
        self.init_table()

        self.move(200, 100)
        self.setWindowTitle("Top 30 Creator")
        self.show()

    def init_table(self):
        """ Initialises the table implementation """
        self.clip_model = ClipListModel()
        self.clip_view.setModel(self.clip_model)

    def on_new_clicked(self):
        """ Event listener for the new menu item """
        self.init_table()

    def on_add_clip_clicked(self):
        """ Event listener for the add clip button """
        directory = os.path.expanduser(top30.SETTINGS.voice_directory())
        filenames, mime  = QtWidgets.QFileDialog.getOpenFileNames(self,
                "Add clip", top30.SETTINGS.song_directory(),
                "Audio(*.mp3 *.ogg);;All Files(*)")
        for filename in filenames:
            self.add_clip(filename)
        self.clip_view.resizeColumnsToContents()

    def on_move_up_clicked(self):
        """ Event listener for the move up button """
        item = self.get_selected_clip()
        if not item == None and item.row() > 0:
            self.clip_model.moveRows(QtCore.QModelIndex(), item.row(),
                                     item.row(), QtCore.QModelIndex(),
                                     item.row() - 1)

    def on_move_down_clicked(self):
        """ Event listener for the move down button """
        item = self.get_selected_clip()
        if not item == None and item.row() < self.clip_model.rowCount() - 1:
            self.clip_model.moveRows(QtCore.QModelIndex(), item.row() + 1,
                                     item.row() + 1, QtCore.QModelIndex(),
                                     item.row())

    def on_delete_clip_clicked(self):
        """ Event listener for the delete clip button """
        item = self.get_selected_clip()
        if not item == None:
            self.clip_model.removeRow(item.row())

    def on_create_clip_clicked(self):
        """ Event listener for the Create Clip button """
        if self.clip_model.rowCount() == 0:
            QtWidgets.QMessageBox.warning(self, "No Clips",
                                          "Please add clips to use")
            return

        self.save_settings()
        rundown_name, file_type = self.save_clip()
        if not rundown_name:
            return

        item = self.clip_model.createIndex(-1, 1)
        item = item.sibling(item.row() + 1, item.column())
        while item.isValid():
            clip = item.data()
            clip_type = item.sibling(item.row(), item.column() - 1).data()
            if item.row() == 0:
                rundown = self.creator.get_start(clip)
            elif item.row() == self.clip_model.rowCount() - 1:
                rundown = self.creator.add_end(clip, rundown)
            elif clip_type == "Song":
                rundown = self.creator.add_song(clip, rundown)
            else:
                rundown = self.creator.add_voice(clip, rundown)
            item = item.sibling(item.row() + 1, item.column())
        self.creator.export(rundown_name, "mp3", rundown)
        QtWidgets.QMessageBox.information(self, "Complete",
                                          "Clip " + rundown_name + " created.")

    def get_selected_clip(self):
        """ Returns the selected clip in the list """
        row = self.clip_view.selectionModel().selectedRows()
        if len(row) == 0:
            return None
        return row[0]

    def add_clip(self, filename):
        """ Adds a clip to the list """
        try:
            time = self.creator.get_start_time(filename)/1000
            time_string = "%02d:%02.1f" % (time / 60, time % 60)
            row = ["Song", filename, time_string]
        except KeyError:
            row = ["Voice", filename, None]
        self.clip_model.appendRow(row)

    def load_settings(self):
        """ Populates the text fields with the apropriate settings """
        clip_length = str(top30.SETTINGS.song_length()/1000)
        voice_start_overlap = str(top30.SETTINGS.voice_start_overlap()/1000)
        voice_end_overlap = str(top30.SETTINGS.voice_end_overlap()/1000)
        self.txt_song_length.setText(clip_length)
        self.txt_voice_start.setText(voice_start_overlap)
        self.txt_voice_end.setText(voice_end_overlap)

    def save_settings(self):
        """ Updates the settings temporarily with the values of the text fields """
        clip_length = float(self.txt_song_length.text()) * 1000
        top30.SETTINGS.set_song_length(clip_length)

        voice_start_overlap = float(self.txt_voice_start.text()) * 1000
        top30.SETTINGS.set_voice_start_overlap(voice_start_overlap)

        voice_end_overlap = float(self.txt_voice_end.text()) * 1000
        top30.SETTINGS.set_voice_end_overlap(voice_end_overlap)

    def save_clip(self):
        """ Prompts the user for the file path to create the new rundown in """
        filename = QtWidgets.QFileDialog.getSaveFileName(self, "Add clip",
                                                         os.path.expanduser("~"),
                                                         "Audio (*.mp3 *.ogg)")
        return filename

class UserInterface:
    def run(self, creator):
        app = QtWidgets.QApplication(sys.argv)
        ex = MainWindow(creator)
        sys.exit(app.exec_())
