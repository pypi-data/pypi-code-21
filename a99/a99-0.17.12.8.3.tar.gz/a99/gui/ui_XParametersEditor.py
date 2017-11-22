# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\XParametersEditor.ui'
#
# Created: Fri Jul 18 20:44:20 2014
#    by: PyQt5 UI code generator 4.10.3
#
# WARNING! All changes made in this file will be lost!

from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
import a99


try:
  _encoding = QApplication.UnicodeUTF8
  def _translate(context, text, disambig):
    return QApplication.translate(context, text, disambig, _encoding)
except AttributeError:
  def _translate(context, text, disambig):
    return QApplication.translate(context, text, disambig)

class Ui_XParametersEditor(object):
  def setupUi(self, XParametersEditor):
    XParametersEditor.setObjectName("XParametersEditor")
    XParametersEditor.setWindowModality(Qt.WindowModal)
    XParametersEditor.resize(446, 62)
    self.horizontalLayout_2 = QHBoxLayout(XParametersEditor)
    self.horizontalLayout_2.setSpacing(2)
    a99.set_margin(self.horizontalLayout_2, 2)
    self.horizontalLayout_2.setObjectName("horizontalLayout_2")
    self.horizontalLayout = QHBoxLayout()
    self.horizontalLayout.setSpacing(2)
    self.horizontalLayout.setObjectName("horizontalLayout")
    self.frame = QFrame(XParametersEditor)
    self.frame.setFrameShape(QFrame.StyledPanel)
    self.frame.setFrameShadow(QFrame.Raised)
    self.frame.setObjectName("frame")
    self.horizontalLayout.addWidget(self.frame)
    self.buttonBox = QDialogButtonBox(XParametersEditor)
    self.buttonBox.setOrientation(Qt.Vertical)
    self.buttonBox.setStandardButtons(QDialogButtonBox.Cancel|QDialogButtonBox.Ok)
    self.buttonBox.setObjectName("buttonBox")
    self.horizontalLayout.addWidget(self.buttonBox)
    self.horizontalLayout_2.addLayout(self.horizontalLayout)

    self.retranslateUi(XParametersEditor)
    self.buttonBox.rejected.connect(XParametersEditor.reject)
    self.buttonBox.accepted.connect(XParametersEditor.accept)
    QMetaObject.connectSlotsByName(XParametersEditor)

  def retranslateUi(self, XParametersEditor):
    XParametersEditor.setWindowTitle(_translate("XParametersEditor", "Parameters Editor", None))

