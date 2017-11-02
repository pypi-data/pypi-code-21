# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtarmsim/ui/multi.ui'
#
# Created: Thu Nov  2 18:25:40 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Multipasos(object):
    def setupUi(self, Multipasos):
        Multipasos.setObjectName("Multipasos")
        Multipasos.resize(400, 101)
        self.pasoslabel = QtGui.QLabel(Multipasos)
        self.pasoslabel.setGeometry(QtCore.QRect(20, 30, 87, 16))
        self.pasoslabel.setObjectName("pasoslabel")
        self.pasos = QtGui.QLineEdit(Multipasos)
        self.pasos.setGeometry(QtCore.QRect(20, 50, 113, 20))
        self.pasos.setObjectName("pasos")
        self.aceptarButton = QtGui.QPushButton(Multipasos)
        self.aceptarButton.setGeometry(QtCore.QRect(280, 20, 75, 23))
        self.aceptarButton.setObjectName("aceptarButton")
        self.cancelarButton = QtGui.QPushButton(Multipasos)
        self.cancelarButton.setGeometry(QtCore.QRect(280, 60, 75, 23))
        self.cancelarButton.setObjectName("cancelarButton")

        self.retranslateUi(Multipasos)
        QtCore.QMetaObject.connectSlotsByName(Multipasos)

    def retranslateUi(self, Multipasos):
        Multipasos.setWindowTitle(QtGui.QApplication.translate("Multipasos", "Múltiples pasos", None, QtGui.QApplication.UnicodeUTF8))
        self.pasoslabel.setText(QtGui.QApplication.translate("Multipasos", "Número de pasos:", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Multipasos", "Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Multipasos", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

