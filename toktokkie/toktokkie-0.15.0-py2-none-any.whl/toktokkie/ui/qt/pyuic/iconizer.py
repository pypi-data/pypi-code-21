# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toktokkie/ui/qt/qt_designer/iconizer.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from __future__ import absolute_import
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_FolderIconizerWindow(object):
    def setupUi(self, FolderIconizerWindow):
        FolderIconizerWindow.setObjectName(u"FolderIconizerWindow")
        FolderIconizerWindow.resize(469, 88)
        FolderIconizerWindow.setMaximumSize(QtCore.QSize(16777215, 88))
        self.centralwidget = QtWidgets.QWidget(FolderIconizerWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.start_button = QtWidgets.QPushButton(self.centralwidget)
        self.start_button.setObjectName(u"start_button")
        self.gridLayout.addWidget(self.start_button, 0, 2, 2, 1)
        self.directory_path_edit = QtWidgets.QLineEdit(self.centralwidget)
        self.directory_path_edit.setObjectName(u"directory_path_edit")
        self.gridLayout.addWidget(self.directory_path_edit, 0, 1, 2, 1)
        self.recursive_check = QtWidgets.QCheckBox(self.centralwidget)
        self.recursive_check.setObjectName(u"recursive_check")
        self.gridLayout.addWidget(self.recursive_check, 1, 0, 1, 1)
        self.browse_directory_button = QtWidgets.QPushButton(self.centralwidget)
        self.browse_directory_button.setObjectName(u"browse_directory_button")
        self.gridLayout.addWidget(self.browse_directory_button, 0, 0, 1, 1)
        FolderIconizerWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(FolderIconizerWindow)
        self.statusbar.setObjectName(u"statusbar")
        FolderIconizerWindow.setStatusBar(self.statusbar)

        self.retranslateUi(FolderIconizerWindow)
        QtCore.QMetaObject.connectSlotsByName(FolderIconizerWindow)

    def retranslateUi(self, FolderIconizerWindow):
        _translate = QtCore.QCoreApplication.translate
        FolderIconizerWindow.setWindowTitle(_translate(u"FolderIconizerWindow", u"Folder Iconizer"))
        self.start_button.setText(_translate(u"FolderIconizerWindow", u"Start"))
        self.recursive_check.setText(_translate(u"FolderIconizerWindow", u"Recursive?"))
        self.browse_directory_button.setText(_translate(u"FolderIconizerWindow", u"Browse"))

