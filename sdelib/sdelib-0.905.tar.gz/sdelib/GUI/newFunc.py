# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'newFunc.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_newFunc(object):
    def setupUi(self, newFunc):
        newFunc.setObjectName("newFunc")
        newFunc.resize(747, 518)
        self.verticalLayout = QtWidgets.QVBoxLayout(newFunc)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtWidgets.QLabel(newFunc)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.tbDescription = QtWidgets.QTextBrowser(newFunc)
        self.tbDescription.setObjectName("tbDescription")
        self.verticalLayout.addWidget(self.tbDescription)
        self.editorHeader = QtWidgets.QLabel(newFunc)
        self.editorHeader.setObjectName("editorHeader")
        self.verticalLayout.addWidget(self.editorHeader)
        self.funcEdit = QtWidgets.QTextEdit(newFunc)
        self.funcEdit.setObjectName("funcEdit")
        self.verticalLayout.addWidget(self.funcEdit)
        self.btnContinue = QtWidgets.QPushButton(newFunc)
        self.btnContinue.setObjectName("btnContinue")
        self.verticalLayout.addWidget(self.btnContinue)

        self.retranslateUi(newFunc)
        QtCore.QMetaObject.connectSlotsByName(newFunc)

    def retranslateUi(self, newFunc):
        _translate = QtCore.QCoreApplication.translate
        newFunc.setWindowTitle(_translate("newFunc", "Input function"))
        self.label.setText(_translate("newFunc", "Description of how to create function:"))
        self.tbDescription.setHtml(_translate("newFunc", "<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
"<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
"p, li { white-space: pre-wrap; }\n"
"</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8pt; font-weight:400; font-style:normal;\">\n"
"<p style=\"-qt-paragraph-type:empty; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\"><br /></p></body></html>"))
        self.editorHeader.setText(_translate("newFunc", "Edit function below:"))
        self.btnContinue.setText(_translate("newFunc", "Validate function (overwrites *function*.py in folder)"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    newFunc = QtWidgets.QWidget()
    ui = Ui_newFunc()
    ui.setupUi(newFunc)
    newFunc.show()
    sys.exit(app.exec_())

