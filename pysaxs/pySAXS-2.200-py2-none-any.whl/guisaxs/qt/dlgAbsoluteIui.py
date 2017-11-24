# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgAbsoluteI.ui'
#
# Created: Thu Jun 11 14:19:02 2015
#      by: PyQt4 UI code generator 4.11.3
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    def _fromUtf8(s):
        return s

try:
    _encoding = QtGui.QApplication.UnicodeUTF8
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
    def _translate(context, text, disambig):
        return QtGui.QApplication.translate(context, text, disambig)

class Ui_dlgSAXSAbsolute(object):
    def setupUi(self, dlgSAXSAbsolute):
        dlgSAXSAbsolute.setObjectName(_fromUtf8("dlgSAXSAbsolute"))
        dlgSAXSAbsolute.resize(498, 690)
        dlgSAXSAbsolute.setMinimumSize(QtCore.QSize(0, 553))
        self.verticalLayout = QtGui.QVBoxLayout(dlgSAXSAbsolute)
        self.verticalLayout.setObjectName(_fromUtf8("verticalLayout"))
        self.labelDataset = QtGui.QLabel(dlgSAXSAbsolute)
        self.labelDataset.setMinimumSize(QtCore.QSize(0, 20))
        self.labelDataset.setBaseSize(QtCore.QSize(0, 0))
        self.labelDataset.setAlignment(QtCore.Qt.AlignJustify|QtCore.Qt.AlignVCenter)
        self.labelDataset.setObjectName(_fromUtf8("labelDataset"))
        self.verticalLayout.addWidget(self.labelDataset)
        self.groupBox = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setLabelAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox)
        self.groupBox_2 = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.groupBox_2)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.checkQrange = QtGui.QCheckBox(self.groupBox_2)
        self.checkQrange.setObjectName(_fromUtf8("checkQrange"))
        self.horizontalLayout.addWidget(self.checkQrange)
        self.checkIrange = QtGui.QCheckBox(self.groupBox_2)
        self.checkIrange.setObjectName(_fromUtf8("checkIrange"))
        self.horizontalLayout.addWidget(self.checkIrange)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBoxBack = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBoxBack.setMaximumSize(QtCore.QSize(16777215, 60))
        self.groupBoxBack.setObjectName(_fromUtf8("groupBoxBack"))
        self.verticalLayout_3 = QtGui.QVBoxLayout(self.groupBoxBack)
        self.verticalLayout_3.setObjectName(_fromUtf8("verticalLayout_3"))
        self.horizontalLayout_3 = QtGui.QHBoxLayout()
        self.horizontalLayout_3.setObjectName(_fromUtf8("horizontalLayout_3"))
        self.checkSubtractBack = QtGui.QCheckBox(self.groupBoxBack)
        self.checkSubtractBack.setMaximumSize(QtCore.QSize(16777215, 20))
        self.checkSubtractBack.setObjectName(_fromUtf8("checkSubtractBack"))
        self.horizontalLayout_3.addWidget(self.checkSubtractBack)
        self.txtBackground = QtGui.QLineEdit(self.groupBoxBack)
        self.txtBackground.setObjectName(_fromUtf8("txtBackground"))
        self.horizontalLayout_3.addWidget(self.txtBackground)
        self.verticalLayout_3.addLayout(self.horizontalLayout_3)
        self.verticalLayout.addWidget(self.groupBoxBack)
        self.groupBoxReference = QtGui.QGroupBox(dlgSAXSAbsolute)
        self.groupBoxReference.setEnabled(True)
        self.groupBoxReference.setObjectName(_fromUtf8("groupBoxReference"))
        self.verticalLayout_2 = QtGui.QVBoxLayout(self.groupBoxReference)
        self.verticalLayout_2.setObjectName(_fromUtf8("verticalLayout_2"))
        self.horizontalLayout_2 = QtGui.QHBoxLayout()
        self.horizontalLayout_2.setObjectName(_fromUtf8("horizontalLayout_2"))
        self.checkSubstractRef = QtGui.QCheckBox(self.groupBoxReference)
        self.checkSubstractRef.setObjectName(_fromUtf8("checkSubstractRef"))
        self.horizontalLayout_2.addWidget(self.checkSubstractRef)
        self.txtReference = QtGui.QLineEdit(self.groupBoxReference)
        self.txtReference.setObjectName(_fromUtf8("txtReference"))
        self.horizontalLayout_2.addWidget(self.txtReference)
        self.verticalLayout_2.addLayout(self.horizontalLayout_2)
        self.verticalLayout.addWidget(self.groupBoxReference)
        self.buttonBox = QtGui.QDialogButtonBox(dlgSAXSAbsolute)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Apply|QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Close)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(dlgSAXSAbsolute)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgSAXSAbsolute.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgSAXSAbsolute)

    def retranslateUi(self, dlgSAXSAbsolute):
        dlgSAXSAbsolute.setWindowTitle(_translate("dlgSAXSAbsolute", "Absolute Intensities", None))
        self.labelDataset.setText(_translate("dlgSAXSAbsolute", "dataset", None))
        self.groupBox.setTitle(_translate("dlgSAXSAbsolute", "Parameters :", None))
        self.groupBox_2.setTitle(_translate("dlgSAXSAbsolute", "Scaling", None))
        self.checkQrange.setText(_translate("dlgSAXSAbsolute", "scaling Q range", None))
        self.checkIrange.setText(_translate("dlgSAXSAbsolute", "scaling I range", None))
        self.groupBoxBack.setTitle(_translate("dlgSAXSAbsolute", "Automatic Background subtraction", None))
        self.checkSubtractBack.setText(_translate("dlgSAXSAbsolute", "subtract background :", None))
        self.groupBoxReference.setTitle(_translate("dlgSAXSAbsolute", "Automatic reference subtraction :", None))
        self.checkSubstractRef.setText(_translate("dlgSAXSAbsolute", "subtract reference :", None))

