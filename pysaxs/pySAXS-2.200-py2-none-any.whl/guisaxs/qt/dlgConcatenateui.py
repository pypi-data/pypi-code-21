# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgConcatenate.ui'
#
# Created: Mon Feb 25 16:33:44 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_concatenateDialog(object):
    def setupUi(self, concatenateDialog):
        concatenateDialog.setObjectName(_fromUtf8("concatenateDialog"))
        concatenateDialog.resize(586, 289)
        self.verticalLayout = QtGui.QVBoxLayout(concatenateDialog)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(concatenateDialog)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.lineEditNewName = QtGui.QLineEdit(concatenateDialog)
        self.lineEditNewName.setObjectName(_fromUtf8("lineEditNewName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.lineEditNewName)
        self.verticalLayout.addLayout(self.formLayout)
        self.tableWidget = QtGui.QTableWidget(concatenateDialog)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setColumnCount(3)
        self.tableWidget.setRowCount(1)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setVerticalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtGui.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        self.verticalLayout.addWidget(self.tableWidget)
        self.gridLayout_2 = QtGui.QGridLayout()
        self.gridLayout_2.setObjectName(_fromUtf8("gridLayout_2"))
        self.pushButtonUP = QtGui.QPushButton(concatenateDialog)
        self.pushButtonUP.setEnabled(True)
        self.pushButtonUP.setMaximumSize(QtCore.QSize(70, 16777215))
        self.pushButtonUP.setObjectName(_fromUtf8("pushButtonUP"))
        self.gridLayout_2.addWidget(self.pushButtonUP, 0, 0, 1, 1)
        self.pushButtonDOWN = QtGui.QPushButton(concatenateDialog)
        self.pushButtonDOWN.setEnabled(True)
        self.pushButtonDOWN.setMaximumSize(QtCore.QSize(70, 16777215))
        self.pushButtonDOWN.setObjectName(_fromUtf8("pushButtonDOWN"))
        self.gridLayout_2.addWidget(self.pushButtonDOWN, 0, 1, 1, 1)
        self.verticalLayout.addLayout(self.gridLayout_2)
        self.buttonBox = QtGui.QDialogButtonBox(concatenateDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(concatenateDialog)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), concatenateDialog.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), concatenateDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(concatenateDialog)

    def retranslateUi(self, concatenateDialog):
        concatenateDialog.setWindowTitle(QtGui.QApplication.translate("concatenateDialog", "Concatenate datas", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("concatenateDialog", "New name :", None, QtGui.QApplication.UnicodeUTF8))
        self.tableWidget.setSortingEnabled(False)
        item = self.tableWidget.verticalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("concatenateDialog", "Nouvelle ligne", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(QtGui.QApplication.translate("concatenateDialog", "Enabled", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(QtGui.QApplication.translate("concatenateDialog", "Qmin", None, QtGui.QApplication.UnicodeUTF8))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(QtGui.QApplication.translate("concatenateDialog", "Qmax", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonUP.setText(QtGui.QApplication.translate("concatenateDialog", "UP", None, QtGui.QApplication.UnicodeUTF8))
        self.pushButtonDOWN.setText(QtGui.QApplication.translate("concatenateDialog", "DOWN", None, QtGui.QApplication.UnicodeUTF8))

