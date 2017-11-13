# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover_plugins_manager/gui_qt/run_dialog.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_RunDialog(object):
    def setupUi(self, RunDialog):
        RunDialog.setObjectName("RunDialog")
        RunDialog.resize(400, 300)
        self.gridLayout = QtWidgets.QGridLayout(RunDialog)
        self.gridLayout.setObjectName("gridLayout")
        self.console = QtWidgets.QWidget(RunDialog)
        self.console.setObjectName("console")
        self.gridLayout.addWidget(self.console, 0, 0, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(RunDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 1, 0, 1, 1)

        self.retranslateUi(RunDialog)
        self.buttonBox.accepted.connect(RunDialog.accept)
        self.buttonBox.rejected.connect(RunDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(RunDialog)

    def retranslateUi(self, RunDialog):
        _translate = QtCore.QCoreApplication.translate
        RunDialog.setWindowTitle(_translate("RunDialog", "Dialog"))

