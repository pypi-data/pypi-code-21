# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgCalculator.ui'
#
# Created: Thu Apr 04 14:59:31 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_Calculator(object):
    def setupUi(self, Calculator):
        Calculator.setObjectName(_fromUtf8("Calculator"))
        Calculator.setWindowModality(QtCore.Qt.WindowModal)
        Calculator.resize(400, 205)
        self.verticalLayout = QtGui.QVBoxLayout(Calculator)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.groupBox = QtGui.QGroupBox(Calculator)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBox)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.lblVariables = QtGui.QLabel(self.groupBox)
        self.lblVariables.setObjectName(_fromUtf8("lblVariables"))
        self.verticalLayout_2.addWidget(self.lblVariables)
        self.label = QtGui.QLabel(self.groupBox)
        self.label.setObjectName(_fromUtf8("label"))
        self.verticalLayout_2.addWidget(self.label)
        self.verticalLayout.addWidget(self.groupBox)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label_2 = QtGui.QLabel(Calculator)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label_2)
        self.EditFormula = QtGui.QLineEdit(Calculator)
        self.EditFormula.setObjectName(_fromUtf8("EditFormula"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.EditFormula)
        self.label_3 = QtGui.QLabel(Calculator)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_3)
        self.EditNewName = QtGui.QLineEdit(Calculator)
        self.EditNewName.setObjectName(_fromUtf8("EditNewName"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.EditNewName)
        self.verticalLayout.addLayout(self.formLayout)
        self.btnApply = QtGui.QPushButton(Calculator)
        self.btnApply.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnApply.setObjectName(_fromUtf8("btnApply"))
        self.verticalLayout.addWidget(self.btnApply)
        self.btnQuit = QtGui.QPushButton(Calculator)
        self.btnQuit.setMaximumSize(QtCore.QSize(100, 16777215))
        self.btnQuit.setObjectName(_fromUtf8("btnQuit"))
        self.verticalLayout.addWidget(self.btnQuit)

        self.retranslateUi(Calculator)
        QtCore.QMetaObject.connectSlotsByName(Calculator)

    def retranslateUi(self, Calculator):
        Calculator.setWindowTitle(QtGui.QApplication.translate("Calculator", "Calculator", None, QtGui.QApplication.UnicodeUTF8))
        self.groupBox.setTitle(QtGui.QApplication.translate("Calculator", "Variables :", None, QtGui.QApplication.UnicodeUTF8))
        self.lblVariables.setText(QtGui.QApplication.translate("Calculator", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("Calculator", "IMPORTANT : if datas have same absissa, errors will be added (if present)  ", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("Calculator", "Formula :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("Calculator", "new dataset name :", None, QtGui.QApplication.UnicodeUTF8))
        self.btnApply.setText(QtGui.QApplication.translate("Calculator", "Apply", None, QtGui.QApplication.UnicodeUTF8))
        self.btnQuit.setText(QtGui.QApplication.translate("Calculator", "Quit", None, QtGui.QApplication.UnicodeUTF8))

