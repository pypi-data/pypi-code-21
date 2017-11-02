# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtarmsim/ui/value.ui'
#
# Created: Thu Nov  2 18:25:40 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Value(object):
    def setupUi(self, Value):
        Value.setObjectName("Value")
        Value.resize(400, 142)
        self.direcLabel = QtGui.QLabel(Value)
        self.direcLabel.setGeometry(QtCore.QRect(20, 20, 151, 16))
        self.direcLabel.setObjectName("direcLabel")
        self.direcLineEdit = QtGui.QLineEdit(Value)
        self.direcLineEdit.setGeometry(QtCore.QRect(20, 40, 201, 20))
        self.direcLineEdit.setObjectName("direcLineEdit")
        self.valueLabel = QtGui.QLabel(Value)
        self.valueLabel.setGeometry(QtCore.QRect(20, 80, 46, 14))
        self.valueLabel.setObjectName("valueLabel")
        self.valueLineEdit = QtGui.QLineEdit(Value)
        self.valueLineEdit.setGeometry(QtCore.QRect(20, 100, 201, 20))
        self.valueLineEdit.setObjectName("valueLineEdit")
        self.aceptarButton = QtGui.QPushButton(Value)
        self.aceptarButton.setGeometry(QtCore.QRect(290, 20, 75, 23))
        self.aceptarButton.setObjectName("aceptarButton")
        self.cancelarButton = QtGui.QPushButton(Value)
        self.cancelarButton.setGeometry(QtCore.QRect(290, 60, 75, 23))
        self.cancelarButton.setObjectName("cancelarButton")

        self.retranslateUi(Value)
        QtCore.QMetaObject.connectSlotsByName(Value)

    def retranslateUi(self, Value):
        Value.setWindowTitle(QtGui.QApplication.translate("Value", "Asignar valor a registro", None, QtGui.QApplication.UnicodeUTF8))
        self.direcLabel.setText(QtGui.QApplication.translate("Value", "Dirección o nombre de registro:", None, QtGui.QApplication.UnicodeUTF8))
        self.valueLabel.setText(QtGui.QApplication.translate("Value", "Valor:", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Value", "Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Value", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

