# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'probRealActions.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_probRealActions(object):
    def setupUi(self, probRealActions):
        probRealActions.setObjectName("probRealActions")
        probRealActions.resize(729, 187)
        self.gridLayout = QtWidgets.QGridLayout(probRealActions)
        self.gridLayout.setObjectName("gridLayout")
        self.txtAction = QtWidgets.QLabel(probRealActions)
        self.txtAction.setObjectName("txtAction")
        self.gridLayout.addWidget(self.txtAction, 0, 0, 1, 1)
        self.cbAction = QtWidgets.QComboBox(probRealActions)
        self.cbAction.setObjectName("cbAction")
        self.cbAction.addItem("")
        self.cbAction.addItem("")
        self.cbAction.addItem("")
        self.cbAction.addItem("")
        self.cbAction.addItem("")
        self.gridLayout.addWidget(self.cbAction, 0, 1, 1, 1)
        self.btnSolver = QtWidgets.QPushButton(probRealActions)
        self.btnSolver.setObjectName("btnSolver")
        self.gridLayout.addWidget(self.btnSolver, 1, 0, 1, 2)
        self.btnExecute = QtWidgets.QPushButton(probRealActions)
        self.btnExecute.setObjectName("btnExecute")
        self.gridLayout.addWidget(self.btnExecute, 2, 0, 1, 2)

        self.retranslateUi(probRealActions)
        QtCore.QMetaObject.connectSlotsByName(probRealActions)

    def retranslateUi(self, probRealActions):
        _translate = QtCore.QCoreApplication.translate
        probRealActions.setWindowTitle(_translate("probRealActions", "Problem realization actions"))
        self.txtAction.setText(_translate("probRealActions", "Choose action to apply to problem realization:"))
        self.cbAction.setItemText(0, _translate("probRealActions", "Solve and plot a single sample path"))
        self.cbAction.setItemText(1, _translate("probRealActions", "Solve and plot average of all sample paths"))
        self.cbAction.setItemText(2, _translate("probRealActions", "Estimate strong order of convergence"))
        self.cbAction.setItemText(3, _translate("probRealActions", "Estimate weak order of convergence"))
        self.cbAction.setItemText(4, _translate("probRealActions", "Show contour plot of stability function(s)"))
        self.btnSolver.setText(_translate("probRealActions", "Select which SDE solvers to use for action"))
        self.btnExecute.setText(_translate("probRealActions", "Execute action"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    probRealActions = QtWidgets.QWidget()
    ui = Ui_probRealActions()
    ui.setupUi(probRealActions)
    probRealActions.show()
    sys.exit(app.exec_())

