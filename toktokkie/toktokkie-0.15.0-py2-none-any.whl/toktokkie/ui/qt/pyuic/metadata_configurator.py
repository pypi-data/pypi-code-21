# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'toktokkie/ui/qt/qt_designer/metadata_configurator.ui'
#
# Created by: PyQt5 UI code generator 5.8.2
#
# WARNING! All changes made in this file will be lost!

from __future__ import absolute_import
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_MetadataConfigurator(object):
    def setupUi(self, MetadataConfigurator):
        MetadataConfigurator.setObjectName(u"MetadataConfigurator")
        MetadataConfigurator.resize(988, 543)
        self.centralwidget = QtWidgets.QWidget(MetadataConfigurator)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.widget_stack = QtWidgets.QStackedWidget(self.centralwidget)
        self.widget_stack.setEnabled(True)
        self.widget_stack.setFrameShape(QtWidgets.QFrame.WinPanel)
        self.widget_stack.setObjectName(u"widget_stack")
        self.page = QtWidgets.QWidget()
        self.page.setObjectName(u"page")
        self.widget_stack.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setObjectName(u"page_2")
        self.widget_stack.addWidget(self.page_2)
        self.gridLayout.addWidget(self.widget_stack, 1, 3, 3, 1)
        self.media_tree = QtWidgets.QTreeWidget(self.centralwidget)
        self.media_tree.setMaximumSize(QtCore.QSize(350, 16777215))
        self.media_tree.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.media_tree.setAcceptDrops(False)
        self.media_tree.setObjectName(u"media_tree")
        self.gridLayout.addWidget(self.media_tree, 1, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.centralwidget)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.frame.sizePolicy().hasHeightForWidth())
        self.frame.setSizePolicy(sizePolicy)
        self.frame.setMaximumSize(QtCore.QSize(350, 16777215))
        self.frame.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName(u"frame")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName(u"gridLayout_2")
        self.add_new_button = QtWidgets.QPushButton(self.frame)
        self.add_new_button.setObjectName(u"add_new_button")
        self.gridLayout_2.addWidget(self.add_new_button, 1, 0, 1, 1)
        self.add_new_edit = QtWidgets.QLineEdit(self.frame)
        self.add_new_edit.setObjectName(u"add_new_edit")
        self.gridLayout_2.addWidget(self.add_new_edit, 1, 1, 1, 1)
        self.browse_button = QtWidgets.QPushButton(self.frame)
        self.browse_button.setObjectName(u"browse_button")
        self.gridLayout_2.addWidget(self.browse_button, 1, 2, 1, 1)
        self.remove_button = QtWidgets.QPushButton(self.frame)
        self.remove_button.setObjectName(u"remove_button")
        self.gridLayout_2.addWidget(self.remove_button, 2, 0, 1, 3)
        self.media_directory_list = QtWidgets.QTreeWidget(self.frame)
        self.media_directory_list.setMaximumSize(QtCore.QSize(16777215, 75))
        self.media_directory_list.setObjectName(u"media_directory_list")
        self.gridLayout_2.addWidget(self.media_directory_list, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.frame, 2, 0, 1, 1)
        MetadataConfigurator.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(MetadataConfigurator)
        self.statusbar.setObjectName(u"statusbar")
        MetadataConfigurator.setStatusBar(self.statusbar)

        self.retranslateUi(MetadataConfigurator)
        self.widget_stack.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(MetadataConfigurator)
        MetadataConfigurator.setTabOrder(self.media_tree, self.media_directory_list)
        MetadataConfigurator.setTabOrder(self.media_directory_list, self.add_new_button)
        MetadataConfigurator.setTabOrder(self.add_new_button, self.add_new_edit)
        MetadataConfigurator.setTabOrder(self.add_new_edit, self.browse_button)
        MetadataConfigurator.setTabOrder(self.browse_button, self.remove_button)

    def retranslateUi(self, MetadataConfigurator):
        _translate = QtCore.QCoreApplication.translate
        MetadataConfigurator.setWindowTitle(_translate(u"MetadataConfigurator", u"toktokkie"))
        self.media_tree.headerItem().setText(0, _translate(u"MetadataConfigurator", u"Media"))
        self.add_new_button.setText(_translate(u"MetadataConfigurator", u"Add New"))
        self.browse_button.setText(_translate(u"MetadataConfigurator", u"Browse"))
        self.remove_button.setText(_translate(u"MetadataConfigurator", u"Remove"))
        self.media_directory_list.headerItem().setText(0, _translate(u"MetadataConfigurator", u"Source Directories"))

