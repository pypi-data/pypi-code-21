# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ui/select_list.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from ..qt import QtCore, QtGui, QtWidgets

class Ui_SelectListDialog(object):
    def setupUi(self, SelectListDialog):
        SelectListDialog.setObjectName("SelectListDialog")
        SelectListDialog.resize(335, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(SelectListDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(SelectListDialog)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.listWidget = QtWidgets.QListWidget(SelectListDialog)
        self.listWidget.setObjectName("listWidget")
        self.verticalLayout.addWidget(self.listWidget)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.okButton = QtWidgets.QPushButton(SelectListDialog)
        self.okButton.setObjectName("okButton")
        self.horizontalLayout.addWidget(self.okButton)
        self.cancelButton = QtWidgets.QPushButton(SelectListDialog)
        self.cancelButton.setObjectName("cancelButton")
        self.horizontalLayout.addWidget(self.cancelButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SelectListDialog)
        QtCore.QMetaObject.connectSlotsByName(SelectListDialog)

    def retranslateUi(self, SelectListDialog):
        _translate = QtCore.QCoreApplication.translate
        SelectListDialog.setWindowTitle(_translate("SelectListDialog", "Select your fs2_open_* executable."))
        self.label.setText(_translate("SelectListDialog", "Please select the fs2_open_* file you want to use."))
        self.okButton.setText(_translate("SelectListDialog", "OK"))
        self.cancelButton.setText(_translate("SelectListDialog", "Cancel"))

