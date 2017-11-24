# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgClipQRange.ui'
#
# Created: Thu Jan 17 14:14:52 2013
#      by: PyQt4 UI code generator 4.9.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

try:
    _fromUtf8 = QtCore.QString.fromUtf8
except AttributeError:
    _fromUtf8 = lambda s: s

class Ui_dlgClipQRange(object):
    def setupUi(self, dlgClipQRange):
        dlgClipQRange.setObjectName(_fromUtf8("dlgClipQRange"))
        dlgClipQRange.setWindowModality(QtCore.Qt.NonModal)
        dlgClipQRange.resize(210, 133)
        dlgClipQRange.setModal(True)
        self.formLayout_2 = QtGui.QFormLayout(dlgClipQRange)
        self.formLayout_2.setObjectName(_fromUtf8("formLayout_2"))
        self.buttonBox = QtGui.QDialogButtonBox(dlgClipQRange)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtGui.QDialogButtonBox.Cancel|QtGui.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName(_fromUtf8("buttonBox"))
        self.formLayout_2.setWidget(2, QtGui.QFormLayout.LabelRole, self.buttonBox)
        self.formLayout = QtGui.QFormLayout()
        self.formLayout.setFieldGrowthPolicy(QtGui.QFormLayout.AllNonFixedFieldsGrow)
        self.formLayout.setObjectName(_fromUtf8("formLayout"))
        self.label = QtGui.QLabel(dlgClipQRange)
        self.label.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label.setObjectName(_fromUtf8("label"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.LabelRole, self.label)
        self.labelDataName = QtGui.QLabel(dlgClipQRange)
        self.labelDataName.setObjectName(_fromUtf8("labelDataName"))
        self.formLayout.setWidget(0, QtGui.QFormLayout.FieldRole, self.labelDataName)
        self.label_2 = QtGui.QLabel(dlgClipQRange)
        self.label_2.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_2.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_2)
        self.qmin = QtGui.QLineEdit(dlgClipQRange)
        self.qmin.setObjectName(_fromUtf8("qmin"))
        self.formLayout.setWidget(1, QtGui.QFormLayout.FieldRole, self.qmin)
        self.label_3 = QtGui.QLabel(dlgClipQRange)
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.LabelRole, self.label_3)
        self.qmax = QtGui.QLineEdit(dlgClipQRange)
        self.qmax.setObjectName(_fromUtf8("qmax"))
        self.formLayout.setWidget(2, QtGui.QFormLayout.FieldRole, self.qmax)
        self.formLayout_2.setLayout(0, QtGui.QFormLayout.SpanningRole, self.formLayout)
        self.label_4 = QtGui.QLabel(dlgClipQRange)
        self.label_4.setObjectName(_fromUtf8("label_4"))
        self.formLayout_2.setWidget(1, QtGui.QFormLayout.LabelRole, self.label_4)

        self.retranslateUi(dlgClipQRange)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("accepted()")), dlgClipQRange.accept)
        QtCore.QObject.connect(self.buttonBox, QtCore.SIGNAL(_fromUtf8("rejected()")), dlgClipQRange.reject)
        QtCore.QMetaObject.connectSlotsByName(dlgClipQRange)

    def retranslateUi(self, dlgClipQRange):
        dlgClipQRange.setWindowTitle(QtGui.QApplication.translate("dlgClipQRange", "Clip q range", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("dlgClipQRange", "Datas : ", None, QtGui.QApplication.UnicodeUTF8))
        self.labelDataName.setText(QtGui.QApplication.translate("dlgClipQRange", "TextLabel", None, QtGui.QApplication.UnicodeUTF8))
        self.label_2.setText(QtGui.QApplication.translate("dlgClipQRange", "q min", None, QtGui.QApplication.UnicodeUTF8))
        self.label_3.setText(QtGui.QApplication.translate("dlgClipQRange", "qmax :", None, QtGui.QApplication.UnicodeUTF8))
        self.label_4.setText(QtGui.QApplication.translate("dlgClipQRange", "WARNING : datas will be recalculated !", None, QtGui.QApplication.UnicodeUTF8))

