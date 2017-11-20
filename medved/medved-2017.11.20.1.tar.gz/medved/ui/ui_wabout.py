# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'medved/ui//ui_wabout.ui'
#
# Created by: PyQt5 UI code generator 5.9.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_WAbout(object):
    def setupUi(self, WAbout):
        WAbout.setObjectName("WAbout")
        WAbout.setWindowModality(QtCore.Qt.ApplicationModal)
        WAbout.resize(868, 762)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/medeval"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        WAbout.setWindowIcon(icon)
        WAbout.setLocale(QtCore.QLocale(QtCore.QLocale.English, QtCore.QLocale.UnitedStates))
        self.verticalLayout = QtWidgets.QVBoxLayout(WAbout)
        self.verticalLayout.setObjectName("verticalLayout")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem)
        self.label = QtWidgets.QLabel(WAbout)
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/medeval"))
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        spacerItem1 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_2.addItem(spacerItem1)
        self.verticalLayout.addLayout(self.horizontalLayout_2)
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        spacerItem2 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem2)
        self.aboutLabel = QtWidgets.QLabel(WAbout)
        self.aboutLabel.setOpenExternalLinks(True)
        self.aboutLabel.setTextInteractionFlags(QtCore.Qt.TextBrowserInteraction)
        self.aboutLabel.setObjectName("aboutLabel")
        self.horizontalLayout_3.addWidget(self.aboutLabel)
        spacerItem3 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout_3.addItem(spacerItem3)
        self.verticalLayout.addLayout(self.horizontalLayout_3)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.buttonUpdate = QtWidgets.QPushButton(WAbout)
        self.buttonUpdate.setObjectName("buttonUpdate")
        self.horizontalLayout.addWidget(self.buttonUpdate)
        spacerItem4 = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem4)
        self.aboutQtButton = QtWidgets.QPushButton(WAbout)
        self.aboutQtButton.setObjectName("aboutQtButton")
        self.horizontalLayout.addWidget(self.aboutQtButton)
        self.closeButton = QtWidgets.QPushButton(WAbout)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(WAbout)
        QtCore.QMetaObject.connectSlotsByName(WAbout)

    def retranslateUi(self, WAbout):
        _translate = QtCore.QCoreApplication.translate
        WAbout.setWindowTitle(_translate("WAbout", "About MEDVED"))
        self.aboutLabel.setText(_translate("WAbout", "<html><head/><body><p>MEDVED (Modulation-Enhanced Diffraction Viewer and EDitor)</p><p>(c) 2016-2017, Vadim Dyadkin, SNBL@ESRF</p><p>This program is licensed under GPL v3</p><p>Mercurial repository: <a href=\"https://hg.3lp.cx/medved\"><span style=\" text-decoration: underline; color:#0057ae;\">https://hg.3lp.cx/medved</span></a></p><p>Version: @@</p><p>Mercurial hash: ##</p><p>When you use this software, please quote the following reference:</p><p><a href=\"http://dx.doi.org/10.1107/S2053273316008378\"><span style=\" text-decoration: underline; color:#0057ae;\">http://dx.doi.org/10.1107/S2053273316008378</span></a></p><p>More information at <a href=\"https://soft.snbl.eu\"><span style=\" text-decoration: underline; color:#0057ae;\">https://soft.snbl.eu</span></a></p></body></html>"))
        self.buttonUpdate.setText(_translate("WAbout", "Check updates"))
        self.aboutQtButton.setText(_translate("WAbout", "About Qt"))
        self.closeButton.setText(_translate("WAbout", "Close"))

from . import resources_rc
