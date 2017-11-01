# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/mcommand/mcommand/hosts/frontends/gui_qt/designer/frm_arguments_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def __init__(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(705, 595)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.LBL_PLUGIN_ICON = QtWidgets.QLabel(Dialog)
        self.LBL_PLUGIN_ICON.setMaximumSize(QtCore.QSize(40, 40))
        self.LBL_PLUGIN_ICON.setStyleSheet("background: #C0FFFFFF;\n"
"border-radius: 8px;")
        self.LBL_PLUGIN_ICON.setText("")
        self.LBL_PLUGIN_ICON.setPixmap(QtGui.QPixmap(":/images/resource_files/app.svg"))
        self.LBL_PLUGIN_ICON.setScaledContents(True)
        self.LBL_PLUGIN_ICON.setObjectName("LBL_PLUGIN_ICON")
        self.horizontalLayout_2.addWidget(self.LBL_PLUGIN_ICON)
        self.LBL_PLUGIN_NAME = QtWidgets.QLabel(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding, QtWidgets.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.LBL_PLUGIN_NAME.sizePolicy().hasHeightForWidth())
        self.LBL_PLUGIN_NAME.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.LBL_PLUGIN_NAME.setFont(font)
        self.LBL_PLUGIN_NAME.setObjectName("LBL_PLUGIN_NAME")
        self.horizontalLayout_2.addWidget(self.LBL_PLUGIN_NAME)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.GRID_ARGS = QtWidgets.QGridLayout()
        self.GRID_ARGS.setVerticalSpacing(8)
        self.GRID_ARGS.setObjectName("GRID_ARGS")
        self.verticalLayout.addLayout(self.GRID_ARGS)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.BTN_MORE = QtWidgets.QPushButton(Dialog)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.BTN_MORE.sizePolicy().hasHeightForWidth())
        self.BTN_MORE.setSizePolicy(sizePolicy)
        self.BTN_MORE.setObjectName("BTN_MORE")
        self.horizontalLayout.addWidget(self.BTN_MORE)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem1)
        self.pushButton = QtWidgets.QPushButton(Dialog)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/images/resource_files/app.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.LBL_PLUGIN_NAME.setText(_translate("Dialog", "TextLabel"))
        self.BTN_MORE.setText(_translate("Dialog", "..."))
        self.pushButton.setText(_translate("Dialog", "Execute"))


