# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'chooseSolvers.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_chooseSolvers(object):
    def setupUi(self, chooseSolvers):
        chooseSolvers.setObjectName("chooseSolvers")
        chooseSolvers.resize(588, 325)
        self.verticalLayout = QtWidgets.QVBoxLayout(chooseSolvers)
        self.verticalLayout.setObjectName("verticalLayout")
        self.txtAction = QtWidgets.QLabel(chooseSolvers)
        self.txtAction.setMinimumSize(QtCore.QSize(281, 0))
        self.txtAction.setMaximumSize(QtCore.QSize(16777215, 19))
        self.txtAction.setObjectName("txtAction")
        self.verticalLayout.addWidget(self.txtAction)
        self.groupBox = QtWidgets.QGroupBox(chooseSolvers)
        self.groupBox.setObjectName("groupBox")
        self.verticalLayout.addWidget(self.groupBox)
        self.btnProceed = QtWidgets.QPushButton(chooseSolvers)
        self.btnProceed.setObjectName("btnProceed")
        self.verticalLayout.addWidget(self.btnProceed)

        self.retranslateUi(chooseSolvers)
        QtCore.QMetaObject.connectSlotsByName(chooseSolvers)

    def retranslateUi(self, chooseSolvers):
        _translate = QtCore.QCoreApplication.translate
        chooseSolvers.setWindowTitle(_translate("chooseSolvers", "Choose solvers for action"))
        self.txtAction.setText(_translate("chooseSolvers", "Action:"))
        self.groupBox.setTitle(_translate("chooseSolvers", "List of solvers"))
        self.btnProceed.setText(_translate("chooseSolvers", "Proceed"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    chooseSolvers = QtWidgets.QWidget()
    ui = Ui_chooseSolvers()
    ui.setupUi(chooseSolvers)
    chooseSolvers.show()
    sys.exit(app.exec_())

