# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newSpec.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newSpec(object):
    def setupUi(self, newSpec):
        newSpec.setObjectName("newSpec")
        newSpec.resize(707, 752)
        self.gridLayout = QtWidgets.QGridLayout(newSpec)
        self.gridLayout.setObjectName("gridLayout")
        self.label_2 = QtWidgets.QLabel(newSpec)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 0, 0, 1, 2)
        self.txtHeader = QtWidgets.QLabel(newSpec)
        self.txtHeader.setObjectName("txtHeader")
        self.gridLayout.addWidget(self.txtHeader, 2, 0, 1, 1)
        self.newSpec_2 = QtWidgets.QTextBrowser(newSpec)
        self.newSpec_2.setMinimumSize(QtCore.QSize(641, 261))
        self.newSpec_2.setObjectName("newSpec_2")
        self.gridLayout.addWidget(self.newSpec_2, 1, 0, 1, 2)
        self.leName = QtWidgets.QLineEdit(newSpec)
        self.leName.setObjectName("leName")
        self.gridLayout.addWidget(self.leName, 2, 1, 1, 1)
        self.txtDimdX = QtWidgets.QLabel(newSpec)
        self.txtDimdX.setObjectName("txtDimdX")
        self.gridLayout.addWidget(self.txtDimdX, 3, 0, 1, 1)
        self.leDimdX = QtWidgets.QLineEdit(newSpec)
        self.leDimdX.setObjectName("leDimdX")
        self.gridLayout.addWidget(self.leDimdX, 3, 1, 1, 1)
        self.label = QtWidgets.QLabel(newSpec)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 6, 0, 1, 2)
        self.checkTrue = QtWidgets.QCheckBox(newSpec)
        self.checkTrue.setObjectName("checkTrue")
        self.gridLayout.addWidget(self.checkTrue, 7, 0, 1, 2)
        self.txtNumWien = QtWidgets.QLabel(newSpec)
        self.txtNumWien.setObjectName("txtNumWien")
        self.gridLayout.addWidget(self.txtNumWien, 4, 0, 1, 1)
        self.leNumWien = QtWidgets.QLineEdit(newSpec)
        self.leNumWien.setObjectName("leNumWien")
        self.gridLayout.addWidget(self.leNumWien, 4, 1, 1, 1)
        self.checkTest = QtWidgets.QCheckBox(newSpec)
        self.checkTest.setObjectName("checkTest")
        self.gridLayout.addWidget(self.checkTest, 9, 0, 1, 2)
        self.cbTrue = QtWidgets.QComboBox(newSpec)
        self.cbTrue.setEnabled(False)
        self.cbTrue.setObjectName("cbTrue")
        self.cbTrue.addItem("")
        self.gridLayout.addWidget(self.cbTrue, 8, 0, 1, 2)
        self.btnFolder = QtWidgets.QPushButton(newSpec)
        self.btnFolder.setObjectName("btnFolder")
        self.gridLayout.addWidget(self.btnFolder, 5, 0, 1, 2)
        self.cbFunction = QtWidgets.QComboBox(newSpec)
        self.cbFunction.setObjectName("cbFunction")
        self.cbFunction.addItem("")
        self.cbFunction.addItem("")
        self.cbFunction.addItem("")
        self.cbFunction.addItem("")
        self.cbFunction.addItem("")
        self.gridLayout.addWidget(self.cbFunction, 11, 1, 1, 1)
        self.txtFunc = QtWidgets.QLabel(newSpec)
        self.txtFunc.setObjectName("txtFunc")
        self.gridLayout.addWidget(self.txtFunc, 11, 0, 1, 1)
        self.btnNewFunc = QtWidgets.QPushButton(newSpec)
        self.btnNewFunc.setObjectName("btnNewFunc")
        self.gridLayout.addWidget(self.btnNewFunc, 12, 1, 1, 1)
        self.btnOpenFunc = QtWidgets.QPushButton(newSpec)
        self.btnOpenFunc.setObjectName("btnOpenFunc")
        self.gridLayout.addWidget(self.btnOpenFunc, 12, 0, 1, 1)
        self.btnCreate = QtWidgets.QPushButton(newSpec)
        self.btnCreate.setObjectName("btnCreate")
        self.gridLayout.addWidget(self.btnCreate, 13, 0, 1, 2)
        self.txtBtn = QtWidgets.QLabel(newSpec)
        self.txtBtn.setObjectName("txtBtn")
        self.gridLayout.addWidget(self.txtBtn, 10, 0, 1, 2)

        self.retranslateUi(newSpec)
        QtCore.QMetaObject.connectSlotsByName(newSpec)
        newSpec.setTabOrder(self.leName, self.leDimdX)
        newSpec.setTabOrder(self.leDimdX, self.leNumWien)
        newSpec.setTabOrder(self.leNumWien, self.btnFolder)
        newSpec.setTabOrder(self.btnFolder, self.checkTrue)
        newSpec.setTabOrder(self.checkTrue, self.cbTrue)
        newSpec.setTabOrder(self.cbTrue, self.checkTest)
        newSpec.setTabOrder(self.checkTest, self.btnCreate)
        newSpec.setTabOrder(self.btnCreate, self.newSpec_2)

    def retranslateUi(self, newSpec):
        _translate = QtCore.QCoreApplication.translate
        newSpec.setWindowTitle(_translate("newSpec", "Create new problem specification"))
        self.label_2.setText(_translate("newSpec", "<html><head/><body><p><span style=\" font-weight:600;\">Description of how to create a problem specification:</span></p></body></html>"))
        self.txtHeader.setText(_translate("newSpec", "Name of problem specification:"))
        self.newSpec_2.setHtml(_translate("newSpec", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Create new problem specification object by choosing a folder which contains a f and g script for f and g functions of the SDE dX = f(X,t)dt + sum[g_k(X,t)dW_k]. To create the problem specification, you must create a .py file that contains an f-function and a .py file that contains a list g of k functions, these are then stored in the folder.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">The template for f and g features some commented out options, but the default uncommented SDE is dX = I*X*dt + sum_k=0^n[I*X*dW_k/n]. Originally multiple templates existed, but simply having a trivial template that is easy to alter proved more flexible.</p>\n"
"<p style=\" margin-top:12px; margin-bottom:12px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">An analytical solution can be imbedded into the problem if &quot;Imbed true solution&quot; is checked. This requires that the SDE is autonomous and multiplicative, meaning dX(t) = FX(t)dt + sum_{k=1}^mG_k(X(t))dW_k(t). See Mao (2007, p. 101) for true solution derivation.</p></body></html>"))
        self.leName.setText(_translate("newSpec", "New SDE"))
        self.txtDimdX.setText(_translate("newSpec", "Dimension of dX:"))
        self.label.setText(_translate("newSpec", "<html><head/><body><p><span style=\" font-weight:600;\">Restrictions on SDE for further functionality</span></p></body></html>"))
        self.checkTrue.setText(_translate("newSpec", "Imbed analytical solution to object. Requires the SDE is among the available options below."))
        self.txtNumWien.setText(_translate("newSpec", "Number of Wiener processes:"))
        self.checkTest.setText(_translate("newSpec", "Scalar test equation dX = aXdt + bXdW where a,b are constants. Allows stability analysis."))
        self.cbTrue.setItemText(0, _translate("newSpec", "Autonomous and multiplicative"))
        self.btnFolder.setText(_translate("newSpec", "Select or create folder to store functions"))
        self.cbFunction.setItemText(0, _translate("newSpec", "f"))
        self.cbFunction.setItemText(1, _translate("newSpec", "g"))
        self.cbFunction.setItemText(2, _translate("newSpec", "g1"))
        self.cbFunction.setItemText(3, _translate("newSpec", "True solution"))
        self.cbFunction.setItemText(4, _translate("newSpec", "Expected value of solution"))
        self.txtFunc.setText(_translate("newSpec", "Choose function:"))
        self.btnNewFunc.setText(_translate("newSpec", "Create new function"))
        self.btnOpenFunc.setText(_translate("newSpec", "Open function from file"))
        self.btnCreate.setText(_translate("newSpec", "Create problem specification and continue to problem realization mode"))
        self.txtBtn.setText(_translate("newSpec", "<html><head/><body><p><span style=\" font-weight:600;\">Create internal functions:</span></p></body></html>"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    newSpec = QtWidgets.QWidget()
    ui = Ui_newSpec()
    ui.setupUi(newSpec)
    newSpec.show()
    sys.exit(app.exec_())

