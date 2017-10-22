# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'mainwindow.ui'
#
# Created by: PyQt4 UI code generator 4.11.4
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

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName(_fromUtf8("MainWindow"))
        MainWindow.setEnabled(True)
        MainWindow.resize(442, 333)
        self.centralwidget = QtGui.QWidget(MainWindow)
        self.centralwidget.setObjectName(_fromUtf8("centralwidget"))
        self.layoutWidget_3 = QtGui.QWidget(self.centralwidget)
        self.layoutWidget_3.setGeometry(QtCore.QRect(10, -30, 701, 31))
        self.layoutWidget_3.setObjectName(_fromUtf8("layoutWidget_3"))
        self.gridLayout_7 = QtGui.QGridLayout(self.layoutWidget_3)
        self.gridLayout_7.setObjectName(_fromUtf8("gridLayout_7"))
        self.line_2 = QtGui.QFrame(self.layoutWidget_3)
        self.line_2.setFrameShape(QtGui.QFrame.HLine)
        self.line_2.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_2.setObjectName(_fromUtf8("line_2"))
        self.gridLayout_7.addWidget(self.line_2, 2, 0, 1, 1)
        self.label_16 = QtGui.QLabel(self.layoutWidget_3)
        self.label_16.setObjectName(_fromUtf8("label_16"))
        self.gridLayout_7.addWidget(self.label_16, 1, 0, 1, 1)
        self.pushButton_SCMS = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SCMS.setGeometry(QtCore.QRect(10, 60, 181, 23))
        self.pushButton_SCMS.setObjectName(_fromUtf8("pushButton_SCMS"))
        self.label = QtGui.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(10, 40, 81, 16))
        self.label.setObjectName(_fromUtf8("label"))
        self.line_7 = QtGui.QFrame(self.centralwidget)
        self.line_7.setGeometry(QtCore.QRect(10, 20, 411, 20))
        self.line_7.setFrameShape(QtGui.QFrame.HLine)
        self.line_7.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_7.setObjectName(_fromUtf8("line_7"))
        self.label_2 = QtGui.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(150, 10, 151, 16))
        self.label_2.setObjectName(_fromUtf8("label_2"))
        self.line = QtGui.QFrame(self.centralwidget)
        self.line.setGeometry(QtCore.QRect(200, 40, 20, 101))
        self.line.setFrameShape(QtGui.QFrame.VLine)
        self.line.setFrameShadow(QtGui.QFrame.Sunken)
        self.line.setObjectName(_fromUtf8("line"))
        self.label_3 = QtGui.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(240, 40, 61, 16))
        self.label_3.setObjectName(_fromUtf8("label_3"))
        self.pushButton_SSSB = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SSSB.setGeometry(QtCore.QRect(230, 60, 181, 23))
        self.pushButton_SSSB.setObjectName(_fromUtf8("pushButton_SSSB"))
        self.pushButton_SSMS = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SSMS.setGeometry(QtCore.QRect(230, 90, 181, 23))
        self.pushButton_SSMS.setObjectName(_fromUtf8("pushButton_SSMS"))
        self.pushButton_SCP = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SCP.setGeometry(QtCore.QRect(10, 90, 181, 23))
        self.pushButton_SCP.setObjectName(_fromUtf8("pushButton_SCP"))
        self.pushButton_SeePy = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SeePy.setGeometry(QtCore.QRect(10, 180, 401, 23))
        self.pushButton_SeePy.setObjectName(_fromUtf8("pushButton_SeePy"))
        self.pushButton_Py4Structure = QtGui.QPushButton(self.centralwidget)
        self.pushButton_Py4Structure.setGeometry(QtCore.QRect(10, 210, 401, 23))
        self.pushButton_Py4Structure.setObjectName(_fromUtf8("pushButton_Py4Structure"))
        self.pushButton_SSBC = QtGui.QPushButton(self.centralwidget)
        self.pushButton_SSBC.setGeometry(QtCore.QRect(230, 120, 181, 23))
        self.pushButton_SSBC.setObjectName(_fromUtf8("pushButton_SSBC"))
        self.line_8 = QtGui.QFrame(self.centralwidget)
        self.line_8.setGeometry(QtCore.QRect(10, 150, 411, 20))
        self.line_8.setFrameShape(QtGui.QFrame.HLine)
        self.line_8.setFrameShadow(QtGui.QFrame.Sunken)
        self.line_8.setObjectName(_fromUtf8("line_8"))
        self.pushButton_DxfStructure = QtGui.QPushButton(self.centralwidget)
        self.pushButton_DxfStructure.setGeometry(QtCore.QRect(10, 240, 401, 23))
        self.pushButton_DxfStructure.setObjectName(_fromUtf8("pushButton_DxfStructure"))
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusbar = QtGui.QStatusBar(MainWindow)
        self.statusbar.setObjectName(_fromUtf8("statusbar"))
        MainWindow.setStatusBar(self.statusbar)
        self.menubar = QtGui.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 442, 28))
        self.menubar.setObjectName(_fromUtf8("menubar"))
        self.menuMenu = QtGui.QMenu(self.menubar)
        self.menuMenu.setEnabled(True)
        self.menuMenu.setObjectName(_fromUtf8("menuMenu"))
        MainWindow.setMenuBar(self.menubar)
        self.actionAbout_STRUTHON_CENCRERE_MONO = QtGui.QAction(MainWindow)
        self.actionAbout_STRUTHON_CENCRERE_MONO.setObjectName(_fromUtf8("actionAbout_STRUTHON_CENCRERE_MONO"))
        self.actionAbout = QtGui.QAction(MainWindow)
        self.actionAbout.setObjectName(_fromUtf8("actionAbout"))
        self.actionCheck_for_updates = QtGui.QAction(MainWindow)
        self.actionCheck_for_updates.setObjectName(_fromUtf8("actionCheck_for_updates"))
        self.menuMenu.addAction(self.actionAbout)
        self.menuMenu.addAction(self.actionCheck_for_updates)
        self.menubar.addAction(self.menuMenu.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(_translate("MainWindow", "APPNAME", None))
        self.label_16.setText(_translate("MainWindow", "Section properties", None))
        self.pushButton_SCMS.setText(_translate("MainWindow", "ConcreteMonoSection", None))
        self.label.setText(_translate("MainWindow", "CONCRETE", None))
        self.label_2.setText(_translate("MainWindow", "AVILABLE APPLICATIONS", None))
        self.label_3.setText(_translate("MainWindow", "STEEL", None))
        self.pushButton_SSSB.setText(_translate("MainWindow", "SteelSectionBrowser", None))
        self.pushButton_SSMS.setText(_translate("MainWindow", "SteelMonoSection", None))
        self.pushButton_SCP.setText(_translate("MainWindow", "ConcretePanel", None))
        self.pushButton_SeePy.setText(_translate("MainWindow", "SeePy", None))
        self.pushButton_Py4Structure.setText(_translate("MainWindow", "Py4Structure", None))
        self.pushButton_SSBC.setText(_translate("MainWindow", "SteelBoltedConnection", None))
        self.pushButton_DxfStructure.setText(_translate("MainWindow", "DxfStructure", None))
        self.menuMenu.setTitle(_translate("MainWindow", "He&lp", None))
        self.actionAbout_STRUTHON_CENCRERE_MONO.setText(_translate("MainWindow", "About STRUTHON CENCRERE MONO", None))
        self.actionAbout.setText(_translate("MainWindow", "&About", None))
        self.actionCheck_for_updates.setText(_translate("MainWindow", "&Check for updates", None))

