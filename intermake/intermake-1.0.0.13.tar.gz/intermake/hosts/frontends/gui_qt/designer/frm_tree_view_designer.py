# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/mcommand/mcommand/hosts/frontends/gui_qt/designer/frm_tree_view_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(875, 758)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.LBL_MAIN = QtWidgets.QLabel(Dialog)
        self.LBL_MAIN.setObjectName("LBL_MAIN")
        self.verticalLayout.addWidget(self.LBL_MAIN)
        self.HOZ_TOOLBAR = QtWidgets.QHBoxLayout()
        self.HOZ_TOOLBAR.setObjectName("HOZ_TOOLBAR")
        self.verticalLayout.addLayout(self.HOZ_TOOLBAR)
        self.splitter = QtWidgets.QSplitter(Dialog)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.TVW_MAIN = QtWidgets.QTreeWidget(self.splitter)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(2)
        sizePolicy.setHeightForWidth(self.TVW_MAIN.sizePolicy().hasHeightForWidth())
        self.TVW_MAIN.setSizePolicy(sizePolicy)
        self.TVW_MAIN.setObjectName("TVW_MAIN")
        self.TVW_MAIN.headerItem().setText(0, "1")
        self.TXT_MAIN = QtWidgets.QTextEdit(self.splitter)
        self.TXT_MAIN.setReadOnly(True)
        self.TXT_MAIN.setObjectName("TXT_MAIN")
        self.verticalLayout.addWidget(self.splitter)
        self.BTNBOX_MAIN = QtWidgets.QDialogButtonBox(Dialog)
        self.BTNBOX_MAIN.setOrientation(QtCore.Qt.Horizontal)
        self.BTNBOX_MAIN.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.BTNBOX_MAIN.setObjectName("BTNBOX_MAIN")
        self.verticalLayout.addWidget(self.BTNBOX_MAIN)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_MAIN.setText(_translate("Dialog", "Label"))

import resources_rc
