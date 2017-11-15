# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'layout_display/layout_display.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_LayoutDisplay(object):
    def setupUi(self, LayoutDisplay):
        LayoutDisplay.setObjectName("LayoutDisplay")
        LayoutDisplay.resize(350, 200)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(LayoutDisplay.sizePolicy().hasHeightForWidth())
        LayoutDisplay.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Monospace")
        LayoutDisplay.setFont(font)
        LayoutDisplay.setSizeGripEnabled(True)
        LayoutDisplay.setModal(False)
        self.verticalLayout = QtWidgets.QVBoxLayout(LayoutDisplay)
        self.verticalLayout.setObjectName("verticalLayout")

        self.retranslateUi(LayoutDisplay)
        QtCore.QMetaObject.connectSlotsByName(LayoutDisplay)

    def retranslateUi(self, LayoutDisplay):
        _translate = QtCore.QCoreApplication.translate
        LayoutDisplay.setWindowTitle(_translate("LayoutDisplay", "Plover: Layout Display"))

from . import resources_rc
