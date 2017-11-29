# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/gogextract.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_GogExtractDialog(object):
    def setupUi(self, GogExtractDialog):
        GogExtractDialog.setObjectName("GogExtractDialog")
        GogExtractDialog.resize(455, 174)
        self.verticalLayout = QtWidgets.QVBoxLayout(GogExtractDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(GogExtractDialog)
        self.label_3.setWordWrap(True)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.destPath = QtWidgets.QLineEdit(GogExtractDialog)
        self.destPath.setObjectName("destPath")
        self.gridLayout_2.addWidget(self.destPath, 6, 1, 1, 1)
        self.label = QtWidgets.QLabel(GogExtractDialog)
        self.label.setObjectName("label")
        self.gridLayout_2.addWidget(self.label, 3, 0, 1, 1)
        self.label_2 = QtWidgets.QLabel(GogExtractDialog)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 6, 0, 1, 1)
        self.gogPath = QtWidgets.QLineEdit(GogExtractDialog)
        self.gogPath.setObjectName("gogPath")
        self.gridLayout_2.addWidget(self.gogPath, 3, 1, 1, 1)
        self.gogButton = QtWidgets.QPushButton(GogExtractDialog)
        self.gogButton.setObjectName("gogButton")
        self.gridLayout_2.addWidget(self.gogButton, 3, 2, 1, 1)
        self.destButton = QtWidgets.QPushButton(GogExtractDialog)
        self.destButton.setObjectName("destButton")
        self.gridLayout_2.addWidget(self.destButton, 6, 2, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.cancelButton = QtWidgets.QPushButton(GogExtractDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.installButton = QtWidgets.QPushButton(GogExtractDialog)
        self.installButton.setEnabled(False)
        self.installButton.setObjectName("installButton")
        self.horizontalLayout.addWidget(self.installButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(GogExtractDialog)
        QtCore.QMetaObject.connectSlotsByName(GogExtractDialog)

    def retranslateUi(self, GogExtractDialog):
        _translate = QtCore.QCoreApplication.translate
        GogExtractDialog.setWindowTitle(_translate("GogExtractDialog", "Extract from GOG Installer"))
        self.label_3.setText(_translate("GogExtractDialog", "Please select the installer which you downloaded from GOG and a destination directory where FS2 should be installed."))
        self.label.setText(_translate("GogExtractDialog", "GOG Installer:"))
        self.label_2.setText(_translate("GogExtractDialog", "Destination:"))
        self.gogButton.setText(_translate("GogExtractDialog", "..."))
        self.destButton.setText(_translate("GogExtractDialog", "..."))
        self.cancelButton.setText(_translate("GogExtractDialog", "Cancel"))
        self.installButton.setText(_translate("GogExtractDialog", "Install"))

