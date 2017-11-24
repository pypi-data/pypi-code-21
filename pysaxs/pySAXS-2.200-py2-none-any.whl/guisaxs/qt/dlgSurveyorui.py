# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'dlgSurveyor.ui'
#
# Created: Wed Jun 17 15:41:29 2015
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

class Ui_surveyorDialog(object):
    def setupUi(self, surveyorDialog):
        surveyorDialog.setObjectName(_fromUtf8("surveyorDialog"))
        surveyorDialog.resize(551, 524)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(_fromUtf8("../images/eye.png")), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        surveyorDialog.setWindowIcon(icon)
        self.Par = QtGui.QGroupBox(surveyorDialog)
        self.Par.setGeometry(QtCore.QRect(10, 10, 521, 50))
        self.Par.setMinimumSize(QtCore.QSize(0, 50))
        self.Par.setMaximumSize(QtCore.QSize(16777215, 50))
        self.Par.setObjectName(_fromUtf8("Par"))
        self.paramTxt = QtGui.QLineEdit(self.Par)
        self.paramTxt.setGeometry(QtCore.QRect(10, 20, 401, 20))
        self.paramTxt.setObjectName(_fromUtf8("paramTxt"))
        self.paramFileButton = QtGui.QPushButton(self.Par)
        self.paramFileButton.setGeometry(QtCore.QRect(420, 20, 41, 23))
        self.paramFileButton.setObjectName(_fromUtf8("paramFileButton"))
        self.paramViewButton = QtGui.QPushButton(self.Par)
        self.paramViewButton.setEnabled(False)
        self.paramViewButton.setGeometry(QtCore.QRect(470, 20, 41, 23))
        self.paramViewButton.setObjectName(_fromUtf8("paramViewButton"))
        self.groupBox_2 = QtGui.QGroupBox(surveyorDialog)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 70, 521, 50))
        self.groupBox_2.setMinimumSize(QtCore.QSize(0, 50))
        self.groupBox_2.setMaximumSize(QtCore.QSize(16777215, 50))
        self.groupBox_2.setObjectName(_fromUtf8("groupBox_2"))
        self.DirTxt = QtGui.QLineEdit(self.groupBox_2)
        self.DirTxt.setGeometry(QtCore.QRect(10, 20, 441, 20))
        self.DirTxt.setObjectName(_fromUtf8("DirTxt"))
        self.changeDirButton = QtGui.QPushButton(self.groupBox_2)
        self.changeDirButton.setGeometry(QtCore.QRect(470, 20, 41, 23))
        self.changeDirButton.setObjectName(_fromUtf8("changeDirButton"))
        self.groupBox = QtGui.QGroupBox(surveyorDialog)
        self.groupBox.setGeometry(QtCore.QRect(10, 130, 521, 111))
        self.groupBox.setObjectName(_fromUtf8("groupBox"))
        self.extensionTxt = QtGui.QLineEdit(self.groupBox)
        self.extensionTxt.setGeometry(QtCore.QRect(172, 20, 101, 20))
        self.extensionTxt.setObjectName(_fromUtf8("extensionTxt"))
        self.labelFileExtensions = QtGui.QLabel(self.groupBox)
        self.labelFileExtensions.setGeometry(QtCore.QRect(70, 20, 101, 16))
        self.labelFileExtensions.setObjectName(_fromUtf8("labelFileExtensions"))
        self.overwriteChk = QtGui.QCheckBox(self.groupBox)
        self.overwriteChk.setGeometry(QtCore.QRect(300, 20, 161, 20))
        self.overwriteChk.setChecked(True)
        self.overwriteChk.setObjectName(_fromUtf8("overwriteChk"))
        self.labelRefreshTime = QtGui.QLabel(self.groupBox)
        self.labelRefreshTime.setGeometry(QtCore.QRect(70, 60, 91, 16))
        self.labelRefreshTime.setObjectName(_fromUtf8("labelRefreshTime"))
        self.refreshTimeTxt = QtGui.QLineEdit(self.groupBox)
        self.refreshTimeTxt.setGeometry(QtCore.QRect(170, 60, 101, 20))
        self.refreshTimeTxt.setObjectName(_fromUtf8("refreshTimeTxt"))
        self.plotChkBox = QtGui.QCheckBox(self.groupBox)
        self.plotChkBox.setGeometry(QtCore.QRect(300, 60, 141, 17))
        self.plotChkBox.setChecked(False)
        self.plotChkBox.setObjectName(_fromUtf8("plotChkBox"))
        self.groupBox_3 = QtGui.QGroupBox(surveyorDialog)
        self.groupBox_3.setGeometry(QtCore.QRect(10, 240, 521, 225))
        self.groupBox_3.setObjectName(_fromUtf8("groupBox_3"))
        self.gridLayout = QtGui.QGridLayout(self.groupBox_3)
        self.gridLayout.setObjectName(_fromUtf8("gridLayout"))
        self.tableWidget = QtGui.QTableWidget(self.groupBox_3)
        self.tableWidget.setAlternatingRowColors(True)
        self.tableWidget.setShowGrid(False)
        self.tableWidget.setColumnCount(0)
        self.tableWidget.setObjectName(_fromUtf8("tableWidget"))
        self.tableWidget.setRowCount(0)
        self.tableWidget.verticalHeader().setVisible(False)
        self.gridLayout.addWidget(self.tableWidget, 0, 0, 1, 1)
        self.horizontalLayoutWidget = QtGui.QWidget(surveyorDialog)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 470, 521, 41))
        self.horizontalLayoutWidget.setObjectName(_fromUtf8("horizontalLayoutWidget"))
        self.horizontalLayout = QtGui.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setMargin(0)
        self.horizontalLayout.setObjectName(_fromUtf8("horizontalLayout"))
        self.buttonClose = QtGui.QDialogButtonBox(self.horizontalLayoutWidget)
        self.buttonClose.setStandardButtons(QtGui.QDialogButtonBox.Close)
        self.buttonClose.setObjectName(_fromUtf8("buttonClose"))
        self.horizontalLayout.addWidget(self.buttonClose)
        self.STARTButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.STARTButton.setObjectName(_fromUtf8("STARTButton"))
        self.horizontalLayout.addWidget(self.STARTButton)
        self.STOPButton = QtGui.QPushButton(self.horizontalLayoutWidget)
        self.STOPButton.setEnabled(True)
        self.STOPButton.setObjectName(_fromUtf8("STOPButton"))
        self.horizontalLayout.addWidget(self.STOPButton)
        self.progressBar = QtGui.QProgressBar(self.horizontalLayoutWidget)
        self.progressBar.setProperty("value", 24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setObjectName(_fromUtf8("progressBar"))
        self.horizontalLayout.addWidget(self.progressBar)

        self.retranslateUi(surveyorDialog)
        QtCore.QObject.connect(self.buttonClose, QtCore.SIGNAL(_fromUtf8("clicked(QAbstractButton*)")), surveyorDialog.close)
        QtCore.QMetaObject.connectSlotsByName(surveyorDialog)

    def retranslateUi(self, surveyorDialog):
        surveyorDialog.setWindowTitle(_translate("surveyorDialog", "Image Surveyor", None))
        self.Par.setTitle(_translate("surveyorDialog", "Parameters file", None))
        self.paramFileButton.setText(_translate("surveyorDialog", "...", None))
        self.paramViewButton.setText(_translate("surveyorDialog", "View", None))
        self.groupBox_2.setTitle(_translate("surveyorDialog", "Directory :", None))
        self.changeDirButton.setText(_translate("surveyorDialog", "...", None))
        self.groupBox.setTitle(_translate("surveyorDialog", "Options :", None))
        self.extensionTxt.setText(_translate("surveyorDialog", "*.tif*", None))
        self.labelFileExtensions.setText(_translate("surveyorDialog", "file extensions :", None))
        self.overwriteChk.setText(_translate("surveyorDialog", "overwrite if already exist", None))
        self.labelRefreshTime.setText(_translate("surveyorDialog", "Refresh time (s) :", None))
        self.refreshTimeTxt.setText(_translate("surveyorDialog", "10", None))
        self.plotChkBox.setText(_translate("surveyorDialog", "Plot", None))
        self.groupBox_3.setTitle(_translate("surveyorDialog", "Files :", None))
        self.tableWidget.setSortingEnabled(True)
        self.STARTButton.setText(_translate("surveyorDialog", "Start", None))
        self.STOPButton.setText(_translate("surveyorDialog", "Stop", None))

