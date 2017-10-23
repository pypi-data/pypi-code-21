# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'calcSolver.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_calcSolver(object):
    def setupUi(self, calcSolver):
        calcSolver.setObjectName("calcSolver")
        calcSolver.resize(419, 300)
        self.verticalLayout = QtWidgets.QVBoxLayout(calcSolver)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_2 = QtWidgets.QLabel(calcSolver)
        self.label_2.setAlignment(QtCore.Qt.AlignCenter)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.cbSolver = QtWidgets.QComboBox(calcSolver)
        self.cbSolver.setObjectName("cbSolver")
        self.cbSolver.addItem("")
        self.cbSolver.addItem("")
        self.cbSolver.addItem("")
        self.cbSolver.addItem("")
        self.cbSolver.addItem("")
        self.verticalLayout.addWidget(self.cbSolver)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.verticalLayout.addItem(spacerItem)
        self.checkPrintNum = QtWidgets.QCheckBox(calcSolver)
        self.checkPrintNum.setObjectName("checkPrintNum")
        self.verticalLayout.addWidget(self.checkPrintNum)
        self.btnGenerateSol = QtWidgets.QPushButton(calcSolver)
        self.btnGenerateSol.setObjectName("btnGenerateSol")
        self.verticalLayout.addWidget(self.btnGenerateSol)
        self.btnSolActions = QtWidgets.QPushButton(calcSolver)
        self.btnSolActions.setObjectName("btnSolActions")
        self.verticalLayout.addWidget(self.btnSolActions)

        self.retranslateUi(calcSolver)
        QtCore.QMetaObject.connectSlotsByName(calcSolver)

    def retranslateUi(self, calcSolver):
        _translate = QtCore.QCoreApplication.translate
        calcSolver.setWindowTitle(_translate("calcSolver", "Calculate solution"))
        self.label_2.setText(_translate("calcSolver", "Calculate solution for chosen solver:"))
        self.cbSolver.setItemText(0, _translate("calcSolver", "itoEM"))
        self.cbSolver.setItemText(1, _translate("calcSolver", "itoMilstein"))
        self.cbSolver.setItemText(2, _translate("calcSolver", "itoTrapezEuler"))
        self.cbSolver.setItemText(3, _translate("calcSolver", "itoBackwardsEuler"))
        self.cbSolver.setItemText(4, _translate("calcSolver", "ito2ndOrder"))
        self.checkPrintNum.setText(_translate("calcSolver", "Print every step. Only recommended for small n"))
        self.btnGenerateSol.setText(_translate("calcSolver", "Solve problem realization with chosen solver"))
        self.btnSolActions.setText(_translate("calcSolver", "Proceed to Solution actions"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    calcSolver = QtWidgets.QWidget()
    ui = Ui_calcSolver()
    ui.setupUi(calcSolver)
    calcSolver.show()
    sys.exit(app.exec_())

