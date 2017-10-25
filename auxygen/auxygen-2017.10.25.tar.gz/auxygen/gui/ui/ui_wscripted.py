# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'auxygen/gui/ui//ui_wscripted.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WScriptEd(object):
    def setupUi(self, WScriptEd):
        WScriptEd.setObjectName("WScriptEd")
        WScriptEd.resize(556, 410)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/scripted"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WScriptEd.setWindowIcon(icon)
        WScriptEd.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(WScriptEd)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.buttonStop = QtWidgets.QPushButton(WScriptEd)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/stop"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.buttonStop.setIcon(icon1)
        self.buttonStop.setObjectName("buttonStop")
        self.horizontalLayout.addWidget(self.buttonStop)
        self.toSeqButton = QtWidgets.QPushButton(WScriptEd)
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap(":/macro"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.toSeqButton.setIcon(icon2)
        self.toSeqButton.setObjectName("toSeqButton")
        self.horizontalLayout.addWidget(self.toSeqButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WScriptEd)
        QtCore.QMetaObject.connectSlotsByName(WScriptEd)

    def retranslateUi(self, WScriptEd):
        _translate = QtCore.QCoreApplication.translate
        WScriptEd.setWindowTitle(_translate("WScriptEd", "Script Editor"))
        self.buttonStop.setText(_translate("WScriptEd", "Stop"))
        self.toSeqButton.setText(_translate("WScriptEd", "To Sequence"))

from . import resources_rc
