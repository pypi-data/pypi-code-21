# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'bubble/bclient/ui/wsaxsparams.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WSaxsParams(object):
    def setupUi(self, WSaxsParams):
        WSaxsParams.setObjectName("WSaxsParams")
        WSaxsParams.resize(578, 236)
        self.formLayout = QtWidgets.QFormLayout(WSaxsParams)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(WSaxsParams)
        self.label.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.thicknessLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.thicknessLineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.thicknessLineEdit.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.thicknessLineEdit.setText("")
        self.thicknessLineEdit.setObjectName("thicknessLineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.thicknessLineEdit)
        self.label_2 = QtWidgets.QLabel(WSaxsParams)
        self.label_2.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.concentrationLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.concentrationLineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.concentrationLineEdit.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.concentrationLineEdit.setText("")
        self.concentrationLineEdit.setObjectName("concentrationLineEdit")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.concentrationLineEdit)
        self.label_3 = QtWidgets.QLabel(WSaxsParams)
        self.label_3.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.label_3.setObjectName("label_3")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.calibrationLineEdit = QtWidgets.QLineEdit(WSaxsParams)
        self.calibrationLineEdit.setMinimumSize(QtCore.QSize(200, 0))
        self.calibrationLineEdit.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.calibrationLineEdit.setText("")
        self.calibrationLineEdit.setObjectName("calibrationLineEdit")
        self.formLayout.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.calibrationLineEdit)
        self.buttonBox = QtWidgets.QDialogButtonBox(WSaxsParams)
        self.buttonBox.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.formLayout.setWidget(3, QtWidgets.QFormLayout.SpanningRole, self.buttonBox)

        self.retranslateUi(WSaxsParams)
        self.buttonBox.accepted.connect(WSaxsParams.accept)
        self.buttonBox.rejected.connect(WSaxsParams.reject)
        QtCore.QMetaObject.connectSlotsByName(WSaxsParams)

    def retranslateUi(self, WSaxsParams):
        _translate = QtCore.QCoreApplication.translate
        WSaxsParams.setWindowTitle(_translate("WSaxsParams", "Advanced SAXS parameters"))
        self.label.setText(_translate("WSaxsParams", "Sample thickness (cm)"))
        self.label_2.setText(_translate("WSaxsParams", "Sample concentration (g/ml)"))
        self.label_3.setText(_translate("WSaxsParams", "<html><head/><body><p>Calibration factor (cm<span style=\" vertical-align:super;\">-1</span>)</p></body></html>"))

