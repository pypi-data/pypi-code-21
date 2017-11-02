# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtarmsim/ui/imprimir.ui'
#
# Created: Thu Nov  2 18:25:40 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Imprimir(object):
    def setupUi(self, Imprimir):
        Imprimir.setObjectName("Imprimir")
        Imprimir.resize(400, 300)
        self.aceptarButton = QtGui.QPushButton(Imprimir)
        self.aceptarButton.setGeometry(QtCore.QRect(300, 30, 75, 23))
        self.aceptarButton.setObjectName("aceptarButton")
        self.cancelarButton = QtGui.QPushButton(Imprimir)
        self.cancelarButton.setGeometry(QtCore.QRect(300, 70, 75, 23))
        self.cancelarButton.setObjectName("cancelarButton")
        self.comboBox = QtGui.QComboBox(Imprimir)
        self.comboBox.setGeometry(QtCore.QRect(30, 40, 181, 21))
        self.comboBox.setObjectName("comboBox")
        self.labelFrom = QtGui.QLabel(Imprimir)
        self.labelFrom.setGeometry(QtCore.QRect(30, 110, 46, 14))
        self.labelFrom.setObjectName("labelFrom")
        self.Tolabel = QtGui.QLabel(Imprimir)
        self.Tolabel.setGeometry(QtCore.QRect(30, 170, 46, 14))
        self.Tolabel.setObjectName("Tolabel")
        self.fromEdit = QtGui.QLineEdit(Imprimir)
        self.fromEdit.setEnabled(False)
        self.fromEdit.setGeometry(QtCore.QRect(30, 130, 121, 20))
        self.fromEdit.setObjectName("fromEdit")
        self.toEdit = QtGui.QLineEdit(Imprimir)
        self.toEdit.setEnabled(False)
        self.toEdit.setGeometry(QtCore.QRect(30, 190, 121, 20))
        self.toEdit.setObjectName("toEdit")

        self.retranslateUi(Imprimir)
        QtCore.QMetaObject.connectSlotsByName(Imprimir)

    def retranslateUi(self, Imprimir):
        Imprimir.setWindowTitle(QtGui.QApplication.translate("Imprimir", "Imprimir valor", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Imprimir", "Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Imprimir", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))
        self.labelFrom.setText(QtGui.QApplication.translate("Imprimir", "From:", None, QtGui.QApplication.UnicodeUTF8))
        self.Tolabel.setText(QtGui.QApplication.translate("Imprimir", "to:", None, QtGui.QApplication.UnicodeUTF8))

