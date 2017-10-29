# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'plover_plugins_manager/gui_qt/manager.ui'
#
# Created by: PyQt5 UI code generator 5.9
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PluginsManager(object):
    def setupUi(self, PluginsManager):
        PluginsManager.setObjectName("PluginsManager")
        PluginsManager.resize(800, 600)
        self.verticalLayout = QtWidgets.QVBoxLayout(PluginsManager)
        self.verticalLayout.setObjectName("verticalLayout")
        self.splitter = QtWidgets.QSplitter(PluginsManager)
        self.splitter.setOrientation(QtCore.Qt.Vertical)
        self.splitter.setObjectName("splitter")
        self.frame = QtWidgets.QFrame(self.splitter)
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.frame)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.table = QtWidgets.QTableWidget(self.frame)
        self.table.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.table.setObjectName("table")
        self.table.setColumnCount(4)
        self.table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.table.setHorizontalHeaderItem(3, item)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.verticalLayout_2.addWidget(self.table)
        self.frame_2 = QtWidgets.QFrame(self.splitter)
        self.frame_2.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame_2.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame_2.setObjectName("frame_2")
        self.gridLayout = QtWidgets.QGridLayout(self.frame_2)
        self.gridLayout.setObjectName("gridLayout")
        self.uninstall_button = QtWidgets.QPushButton(self.frame_2)
        self.uninstall_button.setObjectName("uninstall_button")
        self.gridLayout.addWidget(self.uninstall_button, 0, 1, 1, 1)
        self.restart_button = QtWidgets.QPushButton(self.frame_2)
        self.restart_button.setObjectName("restart_button")
        self.gridLayout.addWidget(self.restart_button, 0, 0, 1, 1)
        self.install_button = QtWidgets.QPushButton(self.frame_2)
        self.install_button.setObjectName("install_button")
        self.gridLayout.addWidget(self.install_button, 0, 2, 1, 1)
        self.info = QtWebEngineWidgets.QWebEngineView(self.frame_2)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.info.sizePolicy().hasHeightForWidth())
        self.info.setSizePolicy(sizePolicy)
        self.info.setProperty("readOnly", True)
        self.info.setProperty("openExternalLinks", False)
        self.info.setObjectName("info")
        self.gridLayout.addWidget(self.info, 6, 0, 1, 3)
        self.verticalLayout.addWidget(self.splitter)

        self.retranslateUi(PluginsManager)
        self.table.itemSelectionChanged.connect(PluginsManager.on_selection_changed)
        self.install_button.clicked.connect(PluginsManager.on_install)
        self.restart_button.clicked.connect(PluginsManager.on_restart)
        self.uninstall_button.clicked.connect(PluginsManager.on_uninstall)
        QtCore.QMetaObject.connectSlotsByName(PluginsManager)

    def retranslateUi(self, PluginsManager):
        _translate = QtCore.QCoreApplication.translate
        PluginsManager.setWindowTitle(_translate("PluginsManager", "Dialog"))
        self.table.setSortingEnabled(True)
        item = self.table.horizontalHeaderItem(0)
        item.setText(_translate("PluginsManager", "State"))
        item = self.table.horizontalHeaderItem(1)
        item.setText(_translate("PluginsManager", "Name"))
        item = self.table.horizontalHeaderItem(2)
        item.setText(_translate("PluginsManager", "Version"))
        item = self.table.horizontalHeaderItem(3)
        item.setText(_translate("PluginsManager", "Summary"))
        self.uninstall_button.setText(_translate("PluginsManager", "Uninstall"))
        self.restart_button.setText(_translate("PluginsManager", "Restart"))
        self.install_button.setText(_translate("PluginsManager", "Install/Update"))

from PyQt5 import QtWebEngineWidgets
from . import resources_rc
