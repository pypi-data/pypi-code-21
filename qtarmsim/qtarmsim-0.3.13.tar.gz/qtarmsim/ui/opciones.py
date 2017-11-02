# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtarmsim/ui/opciones.ui'
#
# Created: Thu Nov  2 18:25:40 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Opciones(object):
    def setupUi(self, Opciones):
        Opciones.setObjectName("Opciones")
        Opciones.resize(400, 300)
        self.actionExplorar = QtGui.QPushButton(Opciones)
        self.actionExplorar.setGeometry(QtCore.QRect(280, 130, 75, 23))
        self.actionExplorar.setObjectName("actionExplorar")
        self.Bare = QtGui.QCheckBox(Opciones)
        self.Bare.setGeometry(QtCore.QRect(41, 51, 99, 18))
        self.Bare.setObjectName("Bare")
        self.Quiet = QtGui.QCheckBox(Opciones)
        self.Quiet.setGeometry(QtCore.QRect(146, 51, 99, 18))
        self.Quiet.setObjectName("Quiet")
        self.Mapped = QtGui.QCheckBox(Opciones)
        self.Mapped.setGeometry(QtCore.QRect(251, 51, 99, 18))
        self.Mapped.setObjectName("Mapped")
        self.Loadtrap = QtGui.QCheckBox(Opciones)
        self.Loadtrap.setGeometry(QtCore.QRect(41, 136, 87, 18))
        self.Loadtrap.setObjectName("Loadtrap")
        self.Directrap = QtGui.QLineEdit(Opciones)
        self.Directrap.setGeometry(QtCore.QRect(134, 135, 133, 20))
        self.Directrap.setObjectName("Directrap")
        self.cancelarButton = QtGui.QPushButton(Opciones)
        self.cancelarButton.setGeometry(QtCore.QRect(290, 240, 75, 23))
        self.cancelarButton.setObjectName("cancelarButton")
        self.buttonBox = QtGui.QPushButton(Opciones)
        self.buttonBox.setGeometry(QtCore.QRect(190, 240, 75, 23))
        self.buttonBox.setObjectName("buttonBox")

        self.retranslateUi(Opciones)
        QtCore.QMetaObject.connectSlotsByName(Opciones)

    def retranslateUi(self, Opciones):
        Opciones.setWindowTitle(QtGui.QApplication.translate("Opciones", "Opciones", None, QtGui.QApplication.UnicodeUTF8))
        self.actionExplorar.setText(QtGui.QApplication.translate("Opciones", "Explorar", None, QtGui.QApplication.UnicodeUTF8))
        self.Bare.setText(QtGui.QApplication.translate("Opciones", "Bare mode", None, QtGui.QApplication.UnicodeUTF8))
        self.Quiet.setText(QtGui.QApplication.translate("Opciones", "Quiet mode", None, QtGui.QApplication.UnicodeUTF8))
        self.Mapped.setText(QtGui.QApplication.translate("Opciones", "Mapped I/O", None, QtGui.QApplication.UnicodeUTF8))
        self.Loadtrap.setText(QtGui.QApplication.translate("Opciones", "Load trap file", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Opciones", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))
        self.buttonBox.setText(QtGui.QApplication.translate("Opciones", "Aceptar", None, QtGui.QApplication.UnicodeUTF8))

