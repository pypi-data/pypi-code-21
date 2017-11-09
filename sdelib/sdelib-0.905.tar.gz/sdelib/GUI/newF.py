# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newF.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newF(object):
    def setupUi(self, newF):
        newF.setObjectName("newF")
        newF.resize(744, 491)
        self.verticalLayout = QtWidgets.QVBoxLayout(newF)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(newF)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tbDescription = QtWidgets.QTextBrowser(newF)
        self.tbDescription.setObjectName("tbDescription")
        self.verticalLayout.addWidget(self.tbDescription)
        self.label_2 = QtWidgets.QLabel(newF)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.fEdit = QtWidgets.QTextEdit(newF)
        self.fEdit.setObjectName("fEdit")
        self.verticalLayout.addWidget(self.fEdit)
        self.btnContinue = QtWidgets.QPushButton(newF)
        self.btnContinue.setObjectName("btnContinue")
        self.verticalLayout.addWidget(self.btnContinue)

        self.retranslateUi(newF)
        QtCore.QMetaObject.connectSlotsByName(newF)

    def retranslateUi(self, newF):
        _translate = QtCore.QCoreApplication.translate
        newF.setWindowTitle(_translate("newF", "Create new f-function in a file"))
        self.label.setText(_translate("newF", "Description of how to create f-function:"))
        self.tbDescription.setHtml(_translate("newF", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">Create f-function in a file by creating a Python-file which contains one method with header def f(X,t). When you press Continue, SDElib tests whether the output of the function has the correct numpy shape, meaning x.shape = (d,) = f(x,t).shape, and imports the function into an SDE-spec object if it does. Correct shape of output is necessary to continue, so for instance f(x,t).shape = (d,1) won\'t continue.</p></body></html>"))
        self.label_2.setText(_translate("newF", "Contents of f.py"))
        self.btnContinue.setText(_translate("newF", "Validate f and continue"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    newF = QtWidgets.QWidget()
    ui = Ui_newF()
    ui.setupUi(newF)
    newF.show()
    sys.exit(app.exec_())

