# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/log_viewer.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_LogDialog(object):
    def setupUi(self, LogDialog):
        LogDialog.setObjectName("LogDialog")
        LogDialog.resize(648, 661)
        LogDialog.setModal(True)
        self.verticalLayout = QtWidgets.QVBoxLayout(LogDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.pathLabel = QtWidgets.QLabel(LogDialog)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.pathLabel.setFont(font)
        self.pathLabel.setObjectName("pathLabel")
        self.verticalLayout.addWidget(self.pathLabel)
        self.content = QtWidgets.QTextBrowser(LogDialog)
        self.content.setObjectName("content")
        self.verticalLayout.addWidget(self.content)
        self.buttonBox = QtWidgets.QDialogButtonBox(LogDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(LogDialog)
        self.buttonBox.accepted.connect(LogDialog.accept)
        self.buttonBox.rejected.connect(LogDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(LogDialog)

    def retranslateUi(self, LogDialog):
        _translate = QtCore.QCoreApplication.translate
        LogDialog.setWindowTitle(_translate("LogDialog", "Log Viewer"))
        self.pathLabel.setText(_translate("LogDialog", "fs2_open.log"))

