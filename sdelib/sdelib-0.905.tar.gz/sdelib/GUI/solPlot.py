# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'solPlot.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_solPlot(object):
    def setupUi(self, solPlot):
        solPlot.setObjectName("solPlot")
        solPlot.setEnabled(True)
        solPlot.resize(803, 366)
        self.verticalLayout = QtWidgets.QVBoxLayout(solPlot)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox = QtWidgets.QGroupBox(solPlot)
        self.groupBox.setObjectName("groupBox")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.groupBox)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.checkSamp = QtWidgets.QCheckBox(self.groupBox)
        self.checkSamp.setEnabled(True)
        self.checkSamp.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkSamp.setChecked(True)
        self.checkSamp.setObjectName("checkSamp")
        self.gridLayout_2.addWidget(self.checkSamp, 0, 0, 1, 1)
        self.leSampNr = QtWidgets.QLineEdit(self.groupBox)
        self.leSampNr.setEnabled(True)
        self.leSampNr.setMaximumSize(QtCore.QSize(75, 25))
        self.leSampNr.setReadOnly(False)
        self.leSampNr.setObjectName("leSampNr")
        self.gridLayout_2.addWidget(self.leSampNr, 0, 1, 1, 1)
        self.txtSampleNr = QtWidgets.QLabel(self.groupBox)
        self.txtSampleNr.setMinimumSize(QtCore.QSize(301, 25))
        self.txtSampleNr.setMaximumSize(QtCore.QSize(301, 25))
        self.txtSampleNr.setObjectName("txtSampleNr")
        self.gridLayout_2.addWidget(self.txtSampleNr, 0, 2, 1, 1)
        self.checkTrue = QtWidgets.QCheckBox(self.groupBox)
        self.checkTrue.setChecked(True)
        self.checkTrue.setObjectName("checkTrue")
        self.gridLayout_2.addWidget(self.checkTrue, 1, 0, 1, 3)
        self.checkSamp.raise_()
        self.txtSampleNr.raise_()
        self.leSampNr.raise_()
        self.checkTrue.raise_()
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(solPlot)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout.setObjectName("gridLayout")
        self.checkMean = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkMean.setEnabled(True)
        self.checkMean.setChecked(False)
        self.checkMean.setObjectName("checkMean")
        self.gridLayout.addWidget(self.checkMean, 0, 0, 1, 1)
        self.checkTrueMean = QtWidgets.QCheckBox(self.groupBox_2)
        self.checkTrueMean.setObjectName("checkTrueMean")
        self.gridLayout.addWidget(self.checkTrueMean, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.btnPlot = QtWidgets.QPushButton(solPlot)
        self.btnPlot.setObjectName("btnPlot")
        self.verticalLayout.addWidget(self.btnPlot)

        self.retranslateUi(solPlot)
        QtCore.QMetaObject.connectSlotsByName(solPlot)

    def retranslateUi(self, solPlot):
        _translate = QtCore.QCoreApplication.translate
        solPlot.setWindowTitle(_translate("solPlot", "Plot solution(s)"))
        self.groupBox.setTitle(_translate("solPlot", "Sample path plot"))
        self.checkSamp.setText(_translate("solPlot", "Include sample path in plot. Sample path nr:"))
        self.leSampNr.setText(_translate("solPlot", "0"))
        self.txtSampleNr.setText(_translate("solPlot", "from 0 to number of simulations."))
        self.checkTrue.setText(_translate("solPlot", "Include true solution of sample path above. trueSol must be in Problem object."))
        self.groupBox_2.setTitle(_translate("solPlot", "Mean plot"))
        self.checkMean.setText(_translate("solPlot", "Include mean of sample paths in plot."))
        self.checkTrueMean.setText(_translate("solPlot", "Include mean of true solutions."))
        self.btnPlot.setText(_translate("solPlot", "Plot solutions"))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    solPlot = QtWidgets.QWidget()
    ui = Ui_solPlot()
    ui.setupUi(solPlot)
    solPlot.show()
    sys.exit(app.exec_())

