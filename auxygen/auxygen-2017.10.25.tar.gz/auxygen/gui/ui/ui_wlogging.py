# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'auxygen/gui/ui//ui_wlogging.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WLogging(object):
    def setupUi(self, WLogging):
        WLogging.setObjectName("WLogging")
        WLogging.resize(690, 208)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/icon"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WLogging.setWindowIcon(icon)
        WLogging.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.horizontalLayout = QtWidgets.QHBoxLayout(WLogging)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.loggingTextEdit = QtWidgets.QPlainTextEdit(WLogging)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        self.loggingTextEdit.setFont(font)
        self.loggingTextEdit.setReadOnly(True)
        self.loggingTextEdit.setObjectName("loggingTextEdit")
        self.horizontalLayout.addWidget(self.loggingTextEdit)

        self.retranslateUi(WLogging)
        QtCore.QMetaObject.connectSlotsByName(WLogging)

    def retranslateUi(self, WLogging):
        _translate = QtCore.QCoreApplication.translate
        WLogging.setWindowTitle(_translate("WLogging", "Logging"))

from . import resources_rc
