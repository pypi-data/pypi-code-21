# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '/Users/martinrusilowicz/work/apps/mcommand/mcommand/hosts/frontends/gui_qt/designer/frm_main_designer.ui'
#
# Created by: PyQt5 UI code generator 5.7
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1229, 945)
        MainWindow.setUnifiedTitleAndToolBarOnMac(False)
        self.centralWidget = QtWidgets.QWidget(MainWindow)
        self.centralWidget.setObjectName("centralWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralWidget)
        self.gridLayout.setContentsMargins(11, 11, 11, 11)
        self.gridLayout.setSpacing(6)
        self.gridLayout.setObjectName("gridLayout")
        self.TAB_MAIN = QtWidgets.QTabWidget(self.centralWidget)
        self.TAB_MAIN.setObjectName("TAB_MAIN")
        self.gridLayout.addWidget(self.TAB_MAIN, 0, 0, 1, 1)
        MainWindow.setCentralWidget(self.centralWidget)
        self.ACTION_HELP_ABOUT = QtWidgets.QAction(MainWindow)
        self.ACTION_HELP_ABOUT.setObjectName("ACTION_HELP_ABOUT")
        self.ACTION_CONFIGURATION = QtWidgets.QAction(MainWindow)
        self.ACTION_CONFIGURATION.setObjectName("ACTION_CONFIGURATION")

        self.retranslateUi(MainWindow)
        self.TAB_MAIN.setCurrentIndex(-1)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.ACTION_HELP_ABOUT.setText(_translate("MainWindow", "ABOUT"))
        self.ACTION_CONFIGURATION.setText(_translate("MainWindow", "CONFIGURATION"))
        self.ACTION_CONFIGURATION.setShortcut(_translate("MainWindow", "F2"))

