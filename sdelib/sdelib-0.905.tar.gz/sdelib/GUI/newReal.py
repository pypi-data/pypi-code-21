# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newReal.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newReal(object):
    def setupUi(self, newReal):
        newReal.setObjectName("newReal")
        newReal.resize(758, 567)
        self.gridLayout = QtWidgets.QGridLayout(newReal)
        self.gridLayout.setObjectName("gridLayout")
        self.txtHeader = QtWidgets.QLabel(newReal)
        font = QtGui.QFont()
        font.setPointSize(10)
        self.txtHeader.setFont(font)
        self.txtHeader.setFrameShadow(QtWidgets.QFrame.Plain)
        self.txtHeader.setAlignment(QtCore.Qt.AlignCenter)
        self.txtHeader.setObjectName("txtHeader")
        self.gridLayout.addWidget(self.txtHeader, 0, 0, 1, 1)
        self.txtSpecHeader = QtWidgets.QLabel(newReal)
        self.txtSpecHeader.setObjectName("txtSpecHeader")
        self.gridLayout.addWidget(self.txtSpecHeader, 1, 0, 1, 1)
        self.txtSpecName = QtWidgets.QLabel(newReal)
        self.txtSpecName.setObjectName("txtSpecName")
        self.gridLayout.addWidget(self.txtSpecName, 1, 1, 1, 2)
        self.cbDefault = QtWidgets.QCheckBox(newReal)
        self.cbDefault.setObjectName("cbDefault")
        self.gridLayout.addWidget(self.cbDefault, 2, 0, 1, 1)
        self.txtNumOfSim = QtWidgets.QLabel(newReal)
        self.txtNumOfSim.setMinimumSize(QtCore.QSize(351, 19))
        self.txtNumOfSim.setObjectName("txtNumOfSim")
        self.gridLayout.addWidget(self.txtNumOfSim, 3, 0, 1, 2)
        self.leNumOfSim = QtWidgets.QLineEdit(newReal)
        self.leNumOfSim.setMaximumSize(QtCore.QSize(361, 25))
        self.leNumOfSim.setObjectName("leNumOfSim")
        self.gridLayout.addWidget(self.leNumOfSim, 3, 2, 1, 1)
        self.txtEndTime = QtWidgets.QLabel(newReal)
        self.txtEndTime.setMinimumSize(QtCore.QSize(351, 19))
        self.txtEndTime.setObjectName("txtEndTime")
        self.gridLayout.addWidget(self.txtEndTime, 4, 0, 1, 2)
        self.leEndTime = QtWidgets.QLineEdit(newReal)
        self.leEndTime.setMaximumSize(QtCore.QSize(361, 25))
        self.leEndTime.setObjectName("leEndTime")
        self.gridLayout.addWidget(self.leEndTime, 4, 2, 1, 1)
        self.tbN = QtWidgets.QTextBrowser(newReal)
        self.tbN.setMaximumSize(QtCore.QSize(732, 80))
        self.tbN.setObjectName("tbN")
        self.gridLayout.addWidget(self.tbN, 5, 0, 1, 3)
        self.leNumOfSamp = QtWidgets.QLineEdit(newReal)
        self.leNumOfSamp.setText("")
        self.leNumOfSamp.setObjectName("leNumOfSamp")
        self.gridLayout.addWidget(self.leNumOfSamp, 6, 0, 1, 3)
        self.textBrowser = QtWidgets.QTextBrowser(newReal)
        self.textBrowser.setMaximumSize(QtCore.QSize(732, 61))
        self.textBrowser.setObjectName("textBrowser")
        self.gridLayout.addWidget(self.textBrowser, 7, 0, 1, 3)
        self.leNFine = QtWidgets.QLineEdit(newReal)
        self.leNFine.setText("")
        self.leNFine.setObjectName("leNFine")
        self.gridLayout.addWidget(self.leNFine, 8, 0, 1, 3)
        self.txtX0 = QtWidgets.QLabel(newReal)
        self.txtX0.setObjectName("txtX0")
        self.gridLayout.addWidget(self.txtX0, 9, 0, 1, 3)
        self.leX0 = QtWidgets.QLineEdit(newReal)
        self.leX0.setObjectName("leX0")
        self.gridLayout.addWidget(self.leX0, 10, 0, 1, 3)
        self.btnProbReal = QtWidgets.QPushButton(newReal)
        self.btnProbReal.setObjectName("btnProbReal")
        self.gridLayout.addWidget(self.btnProbReal, 11, 0, 1, 3)
        self.checkPrint = QtWidgets.QCheckBox(newReal)
        self.checkPrint.setObjectName("checkPrint")
        self.gridLayout.addWidget(self.checkPrint, 2, 1, 1, 2)

        self.retranslateUi(newReal)
        QtCore.QMetaObject.connectSlotsByName(newReal)

    def retranslateUi(self, newReal):
        _translate = QtCore.QCoreApplication.translate
        newReal.setWindowTitle(_translate("newReal", "Problem realization mode"))
        self.txtHeader.setText(_translate("newReal", "Problem realization mode"))
        self.txtSpecHeader.setText(_translate("newReal", "Problem specification name:"))
        self.txtSpecName.setText(_translate("newReal", "TextLabel"))
        self.cbDefault.setText(_translate("newReal", "Default values"))
        self.txtNumOfSim.setToolTip(_translate("newReal", "<html><head/><body><p>Determines the number of sample paths are created. Used for averaging across multiple realizations of the problem for different Wiener process realization.</p></body></html>"))
        self.txtNumOfSim.setText(_translate("newReal", "Number of simulations:"))
        self.txtEndTime.setText(_translate("newReal", "End time T, time interval will be [0,T]"))
        self.tbN.setHtml(_translate("newReal", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">n, the number of time intervals between 0 and T, meaning t = np.linspace(0,T,n+1) so that dt = T/n. n has to be divisible by 16 if you want to do stability analysis. Normally a power of 2 by convention.</p></body></html>"))
        self.textBrowser.setHtml(_translate("newReal", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">nFine, the number of time intervals between 0 and T for exact solution (or approximation of exact solution if no exact solution exists). Has to be divisible by n so that the points of the analytical solution overlap with the numerical solution. Leave empty if true Solution is not to be calculated.</p></body></html>"))
        self.txtX0.setText(_translate("newReal", "Value of X at t=0, different dimensions seperated by comma:"))
        self.btnProbReal.setText(_translate("newReal", "Create problem realization"))
        self.checkPrint.setText(_translate("newReal", "Print each iteration for true solution. Use small nFine"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    newReal = QtWidgets.QWidget()
    ui = Ui_newReal()
    ui.setupUi(newReal)
    newReal.show()
    sys.exit(app.exec_())

