# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file './qtarmsim/ui/ejec.ui'
#
# Created: Thu Nov  2 18:25:40 2017
#      by: pyside-uic 0.2.15 running on PySide 1.2.2
#
# WARNING! All changes made in this file will be lost!

from PySide import QtCore, QtGui

class Ui_Ejecutar(object):
    def setupUi(self, Ejecutar):
        Ejecutar.setObjectName("Ejecutar")
        Ejecutar.resize(400, 172)
        self.adress = QtGui.QLineEdit(Ejecutar)
        self.adress.setGeometry(QtCore.QRect(20, 50, 113, 20))
        self.adress.setToolTip("")
        self.adress.setInputMask("")
        self.adress.setObjectName("adress")
        self.adresslabel = QtGui.QLabel(Ejecutar)
        self.adresslabel.setGeometry(QtCore.QRect(20, 20, 88, 31))
        self.adresslabel.setObjectName("adresslabel")
        self.linelabel = QtGui.QLabel(Ejecutar)
        self.linelabel.setGeometry(QtCore.QRect(20, 80, 98, 16))
        self.linelabel.setObjectName("linelabel")
        self.lineEdit = QtGui.QLineEdit(Ejecutar)
        self.lineEdit.setGeometry(QtCore.QRect(20, 100, 113, 20))
        self.lineEdit.setObjectName("lineEdit")
        self.undefcheckBox = QtGui.QCheckBox(Ejecutar)
        self.undefcheckBox.setGeometry(QtCore.QRect(20, 130, 161, 18))
        self.undefcheckBox.setObjectName("undefcheckBox")
        self.aceptarButton = QtGui.QPushButton(Ejecutar)
        self.aceptarButton.setGeometry(QtCore.QRect(280, 40, 75, 23))
        self.aceptarButton.setObjectName("aceptarButton")
        self.cancelarButton = QtGui.QPushButton(Ejecutar)
        self.cancelarButton.setGeometry(QtCore.QRect(280, 90, 75, 23))
        self.cancelarButton.setObjectName("cancelarButton")

        self.retranslateUi(Ejecutar)
        QtCore.QMetaObject.connectSlotsByName(Ejecutar)

    def retranslateUi(self, Ejecutar):
        Ejecutar.setWindowTitle(QtGui.QApplication.translate("Ejecutar", "Parámatros de ejecución", None, QtGui.QApplication.UnicodeUTF8))
        self.adress.setText(QtGui.QApplication.translate("Ejecutar", "0x00000000", None, QtGui.QApplication.UnicodeUTF8))
        self.adresslabel.setText(QtGui.QApplication.translate("Ejecutar", "Dirección de inicio:", None, QtGui.QApplication.UnicodeUTF8))
        self.linelabel.setText(QtGui.QApplication.translate("Ejecutar", "Línea de instrucción:", None, QtGui.QApplication.UnicodeUTF8))
        self.undefcheckBox.setText(QtGui.QApplication.translate("Ejecutar", "Buscar símbolos no definidos", None, QtGui.QApplication.UnicodeUTF8))
        self.aceptarButton.setText(QtGui.QApplication.translate("Ejecutar", "Aceptar", None, QtGui.QApplication.UnicodeUTF8))
        self.cancelarButton.setText(QtGui.QApplication.translate("Ejecutar", "Cancelar", None, QtGui.QApplication.UnicodeUTF8))

