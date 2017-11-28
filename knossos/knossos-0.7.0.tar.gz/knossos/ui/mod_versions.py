# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/mod_versions.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_ModVersionsDialog(object):
    def setupUi(self, ModVersionsDialog):
        ModVersionsDialog.setObjectName("ModVersionsDialog")
        ModVersionsDialog.resize(400, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(ModVersionsDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(ModVersionsDialog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.versionList = QtWidgets.QListWidget(ModVersionsDialog)
        self.versionList.setObjectName("versionList")
        self.verticalLayout.addWidget(self.versionList)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.applyButton = QtWidgets.QPushButton(ModVersionsDialog)
        self.applyButton.setObjectName("applyButton")
        self.horizontalLayout.addWidget(self.applyButton)
        self.cancelButton = QtWidgets.QPushButton(ModVersionsDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(ModVersionsDialog)
        QtCore.QMetaObject.connectSlotsByName(ModVersionsDialog)

    def retranslateUi(self, ModVersionsDialog):
        _translate = QtCore.QCoreApplication.translate
        ModVersionsDialog.setWindowTitle(_translate("ModVersionsDialog", "Mod versions"))
        self.label.setText(_translate("ModVersionsDialog", "Available versions for {MOD}:"))
        self.applyButton.setText(_translate("ModVersionsDialog", "Apply"))
        self.cancelButton.setText(_translate("ModVersionsDialog", "Cancel"))

