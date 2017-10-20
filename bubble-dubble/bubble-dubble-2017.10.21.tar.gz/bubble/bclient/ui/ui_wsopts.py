# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bubble/bclient/ui/ui_wsopts.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WSOpts(object):
    def setupUi(self, WSOpts):
        WSOpts.setObjectName("WSOpts")
        WSOpts.resize(514, 377)
        WSOpts.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.gridLayout = QtWidgets.QGridLayout(WSOpts)
        self.gridLayout.setObjectName("gridLayout")
        self.checkSA = QtWidgets.QCheckBox(WSOpts)
        self.checkSA.setChecked(True)
        self.checkSA.setObjectName("checkSA")
        self.gridLayout.addWidget(self.checkSA, 0, 0, 1, 1)
        self.checkDouble = QtWidgets.QCheckBox(WSOpts)
        self.checkDouble.setObjectName("checkDouble")
        self.gridLayout.addWidget(self.checkDouble, 1, 0, 1, 1)
        self.checkHalina = QtWidgets.QCheckBox(WSOpts)
        self.checkHalina.setObjectName("checkHalina")
        self.gridLayout.addWidget(self.checkHalina, 2, 0, 1, 1)
        self.checkPol = QtWidgets.QCheckBox(WSOpts)
        self.checkPol.setObjectName("checkPol")
        self.gridLayout.addWidget(self.checkPol, 3, 0, 1, 1)
        self.spinPol = QtWidgets.QDoubleSpinBox(WSOpts)
        self.spinPol.setEnabled(False)
        self.spinPol.setMinimum(-1.0)
        self.spinPol.setMaximum(1.0)
        self.spinPol.setSingleStep(0.01)
        self.spinPol.setProperty("value", 0.99)
        self.spinPol.setObjectName("spinPol")
        self.gridLayout.addWidget(self.spinPol, 3, 1, 1, 1)
        self.checkThreads = QtWidgets.QCheckBox(WSOpts)
        self.checkThreads.setObjectName("checkThreads")
        self.gridLayout.addWidget(self.checkThreads, 4, 0, 1, 1)
        self.spinThreads = QtWidgets.QSpinBox(WSOpts)
        self.spinThreads.setEnabled(False)
        self.spinThreads.setMinimum(1)
        self.spinThreads.setMaximum(50)
        self.spinThreads.setObjectName("spinThreads")
        self.gridLayout.addWidget(self.spinThreads, 4, 1, 1, 1)
        self.checkBins = QtWidgets.QCheckBox(WSOpts)
        self.checkBins.setObjectName("checkBins")
        self.gridLayout.addWidget(self.checkBins, 5, 0, 1, 1)
        self.spinBins = QtWidgets.QSpinBox(WSOpts)
        self.spinBins.setEnabled(False)
        self.spinBins.setMinimum(1)
        self.spinBins.setMaximum(100000)
        self.spinBins.setObjectName("spinBins")
        self.gridLayout.addWidget(self.spinBins, 5, 1, 1, 1)
        self.buttonBox = QtWidgets.QDialogButtonBox(WSOpts)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.gridLayout.addWidget(self.buttonBox, 6, 0, 1, 2)

        self.retranslateUi(WSOpts)
        self.buttonBox.accepted.connect(WSOpts.accept)
        self.buttonBox.rejected.connect(WSOpts.reject)
        QtCore.QMetaObject.connectSlotsByName(WSOpts)

    def retranslateUi(self, WSOpts):
        _translate = QtCore.QCoreApplication.translate
        WSOpts.setWindowTitle(_translate("WSOpts", "Server options"))
        self.checkSA.setText(_translate("WSOpts", "Solid angle correction"))
        self.checkDouble.setText(_translate("WSOpts", "Double precision"))
        self.checkHalina.setText(_translate("WSOpts", "Halina\'s equation for SAXS"))
        self.checkPol.setText(_translate("WSOpts", "Polarization correction"))
        self.checkThreads.setText(_translate("WSOpts", "Number of threads"))
        self.checkBins.setText(_translate("WSOpts", "Number of bins"))

