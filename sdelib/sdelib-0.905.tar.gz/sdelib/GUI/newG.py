# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newG.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newG(object):
    def setupUi(self, newG):
        newG.setObjectName("newG")
        newG.resize(738, 555)
        self.verticalLayout = QtWidgets.QVBoxLayout(newG)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(newG)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tbDescription = QtWidgets.QTextBrowser(newG)
        self.tbDescription.setObjectName("tbDescription")
        self.verticalLayout.addWidget(self.tbDescription)
        self.label_2 = QtWidgets.QLabel(newG)
        self.label_2.setObjectName("label_2")
        self.verticalLayout.addWidget(self.label_2)
        self.gEdit = QtWidgets.QTextEdit(newG)
        self.gEdit.setObjectName("gEdit")
        self.verticalLayout.addWidget(self.gEdit)
        self.btnContinue = QtWidgets.QPushButton(newG)
        self.btnContinue.setObjectName("btnContinue")
        self.verticalLayout.addWidget(self.btnContinue)

        self.retranslateUi(newG)
        QtCore.QMetaObject.connectSlotsByName(newG)

    def retranslateUi(self, newG):
        _translate = QtCore.QCoreApplication.translate
        newG.setWindowTitle(_translate("newG", "Create new g-function in a file"))
        self.label.setText(_translate("newG", "Description of how to create g-function:"))
        self.tbDescription.setHtml(_translate("newG", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">For SDE dX = f(X,t)dt + sum_k=0^m[g_k(X,t)dW_k], provide a .py file containing a list of functions called g where each function has input (X,t). For each g[k], g[k](X,t) must give out an output of shape (d,). This means g_k is a matrix-valued function of dimension d x d that takes in a X-vector with shape (d,) whose output has shape (d,), dW_k is a scalar and therefore g(X,t,k=q)dW_k has shape (d,).</p>\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p>\n"
"<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">If shapes correspond correctly, SDElib adds function into the SDE-spec object and continues. Correct shape of output is necessary to continue.</p></body></html>"))
        self.label_2.setText(_translate("newG", "Contents of g.py"))
        self.btnContinue.setText(_translate("newG", "Validate g and continue"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    newG = QtWidgets.QWidget()
    ui = Ui_newG()
    ui.setupUi(newG)
    newG.show()
    sys.exit(app.exec_())

