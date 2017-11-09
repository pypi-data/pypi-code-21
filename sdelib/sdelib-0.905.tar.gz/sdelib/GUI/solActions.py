# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'solActions.ui'
#
# Created by: PyQt5 UI code generator 5.6
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_solActions(object):
    def setupUi(self, solActions):
        solActions.setObjectName("solActions")
        solActions.setEnabled(True)
        solActions.resize(722, 663)
        self.gridLayout = QtWidgets.QGridLayout(solActions)
        self.gridLayout.setObjectName("gridLayout")
        self.btnPlot = QtWidgets.QPushButton(solActions)
        self.btnPlot.setObjectName("btnPlot")
        self.gridLayout.addWidget(self.btnPlot, 8, 0, 1, 3)
        self.leSampNr = QtWidgets.QLineEdit(solActions)
        self.leSampNr.setEnabled(True)
        self.leSampNr.setMaximumSize(QtCore.QSize(75, 25))
        self.leSampNr.setReadOnly(False)
        self.leSampNr.setObjectName("leSampNr")
        self.gridLayout.addWidget(self.leSampNr, 1, 1, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(solActions)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 7, 0, 1, 1)
        self.checkSamp = QtWidgets.QCheckBox(solActions)
        self.checkSamp.setEnabled(True)
        self.checkSamp.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.checkSamp.setChecked(True)
        self.checkSamp.setObjectName("checkSamp")
        self.gridLayout.addWidget(self.checkSamp, 1, 0, 1, 1)
        self.btnSolutions = QtWidgets.QPushButton(solActions)
        self.btnSolutions.setEnabled(False)
        self.btnSolutions.setObjectName("btnSolutions")
        self.gridLayout.addWidget(self.btnSolutions, 7, 1, 1, 2)
        self.btnStore = QtWidgets.QPushButton(solActions)
        self.btnStore.setObjectName("btnStore")
        self.gridLayout.addWidget(self.btnStore, 9, 0, 1, 3)
        self.checkTrue = QtWidgets.QCheckBox(solActions)
        self.checkTrue.setChecked(True)
        self.checkTrue.setObjectName("checkTrue")
        self.gridLayout.addWidget(self.checkTrue, 2, 0, 1, 2)
        self.txtSampleNr = QtWidgets.QLabel(solActions)
        self.txtSampleNr.setObjectName("txtSampleNr")
        self.gridLayout.addWidget(self.txtSampleNr, 1, 2, 1, 1)
        self.checkMean = QtWidgets.QCheckBox(solActions)
        self.checkMean.setEnabled(True)
        self.checkMean.setChecked(False)
        self.checkMean.setObjectName("checkMean")
        self.gridLayout.addWidget(self.checkMean, 6, 0, 1, 1)
        self.checkTrueMean = QtWidgets.QCheckBox(solActions)
        self.checkTrueMean.setObjectName("checkTrueMean")
        self.gridLayout.addWidget(self.checkTrueMean, 6, 1, 1, 2)

        self.retranslateUi(solActions)
        QtCore.QMetaObject.connectSlotsByName(solActions)
        solActions.setTabOrder(self.checkSamp, self.leSampNr)
        solActions.setTabOrder(self.leSampNr, self.checkTrue)
        solActions.setTabOrder(self.checkTrue, self.checkBox)
        solActions.setTabOrder(self.checkBox, self.btnSolutions)
        solActions.setTabOrder(self.btnSolutions, self.btnPlot)
        solActions.setTabOrder(self.btnPlot, self.btnStore)

    def retranslateUi(self, solActions):
        _translate = QtCore.QCoreApplication.translate
        solActions.setWindowTitle(_translate("solActions", "Actions for calculated solutions"))
        self.btnPlot.setText(_translate("solActions", "Plot solutions"))
        self.leSampNr.setText(_translate("solActions", "0"))
        self.checkBox.setText(_translate("solActions", "Include all numerical solutions in plot."))
        self.checkSamp.setText(_translate("solActions", "Include sample path in plot. Sample path nr:"))
        self.btnSolutions.setText(_translate("solActions", "Choose solutions included in plot"))
        self.btnStore.setText(_translate("solActions", "Store problem and solutions"))
        self.checkTrue.setText(_translate("solActions", "Include true solution of sample path above."))
        self.txtSampleNr.setText(_translate("solActions", "from 0 to number of simulations."))
        self.checkMean.setText(_translate("solActions", "Include mean of sample paths in plot."))
        self.checkTrueMean.setText(_translate("solActions", "Include mean of true solutions."))


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    solActions = QtWidgets.QWidget()
    ui = Ui_solActions()
    ui.setupUi(solActions)
    solActions.show()
    sys.exit(app.exec_())

