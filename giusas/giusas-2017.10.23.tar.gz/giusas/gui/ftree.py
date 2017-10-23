#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import uuid
from PyQt5 import QtCore, QtWidgets
import cryio


class TreeWidget(QtWidgets.QTreeWidget):
    deleteKeySignal = QtCore.pyqtSignal()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Delete:
            self.deleteKeySignal.emit()
        else:
            super().keyPressEvent(event)


class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__uuid = uuid.uuid4()

    def __hash__(self):
        return hash(self.__uuid)


class ItemProxy:
    def __init__(self, openSignal, applySignal):
        self.openSignal = openSignal
        self.applySignal = applySignal
        self.files = []

    def openEmit(self, files=None):
        self.files = files or self.files
        self.openSignal.emit(self.files)

    def removeFile(self, file):
        self.files.remove(file)
        self.openEmit()


class FilesTree(QtWidgets.QWidget):
    openDataSignal = QtCore.pyqtSignal(list)
    applyDataSignal = QtCore.pyqtSignal(bool)
    openBkgSignal = QtCore.pyqtSignal(list)
    applyBkgSignal = QtCore.pyqtSignal(bool)
    openDarkSignal = QtCore.pyqtSignal(list)
    applyDarkSignal = QtCore.pyqtSignal(bool)
    openFloodSignal = QtCore.pyqtSignal(list)
    applyFloodSignal = QtCore.pyqtSignal(bool)
    openSplineSignal = QtCore.pyqtSignal(list)
    applySplineSignal = QtCore.pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.workDir = ''
        self.setWindowTitle('Files')
        self.setUI()
        self.connectSignals()

    def setUI(self):
        self.tree = TreeWidget(self)
        layout = QtWidgets.QGridLayout()
        self.setLayout(layout)
        layout.addWidget(self.tree)
        self.tree.setColumnCount(2)
        headerItem = self.tree.headerItem()
        headerItem.setText(0, 'Files')
        headerItem.setText(1, 'Apply?')
        header = self.tree.header()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(QtWidgets.QHeaderView.ResizeToContents)
        self.dataItem = TreeWidgetItem(self.tree)
        self.dataItem.setText(0, 'Data')
        self.bkgItem = TreeWidgetItem(self.tree)
        self.bkgItem.setText(0, 'Background')
        self.bkgItem.setCheckState(1, QtCore.Qt.Unchecked)
        self.darkItem = TreeWidgetItem(self.tree)
        self.darkItem.setText(0, 'Dark Current')
        self.darkItem.setCheckState(1, QtCore.Qt.Unchecked)
        self.floodItem = TreeWidgetItem(self.tree)
        self.floodItem.setText(0, 'Flat field')
        self.floodItem.setCheckState(1, QtCore.Qt.Unchecked)
        self.splineItem = TreeWidgetItem(self.tree)
        self.splineItem.setText(0, 'Spline')
        self.splineItem.setCheckState(1, QtCore.Qt.Unchecked)
        self.itemSignals = {
            self.dataItem:   ItemProxy(self.openDataSignal, self.applyDataSignal),
            self.bkgItem:    ItemProxy(self.openBkgSignal, self.applyBkgSignal),
            self.darkItem:   ItemProxy(self.openDarkSignal, self.applyDarkSignal),
            self.floodItem:  ItemProxy(self.openFloodSignal, self.applyFloodSignal),
            self.splineItem: ItemProxy(self.openSplineSignal, self.applySplineSignal),
        }

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.tree.itemDoubleClicked.connect(self.itemDoubleClicked)
        self.tree.itemClicked.connect(self.itemClicked)
        self.tree.itemChanged.connect(self.itemChanged)
        self.tree.deleteKeySignal.connect(self.deleteItems)

    def deleteItems(self):
        for item in self.tree.selectedItems():
            if item not in self.itemSignals.keys():
                parent = item.parent()
                # noinspection PyTypeChecker
                parentItem = self.itemSignals[parent]
                parentItem.removeFile(item.text(0))
                parent.removeChild(item)

    def itemChanged(self, item, col):
        if col != 1 or item not in self.itemSignals.keys():
            return
        self.itemSignals[item].applySignal.emit(bool(item.checkState(1)))

    def itemDoubleClicked(self, item, col):
        if col or item not in self.itemSignals.keys():
            return
        # noinspection PyCallByClass,PyTypeChecker
        fs = QtWidgets.QFileDialog.getOpenFileNames(self, f'Select {item.text(0)} files',
                                                    self.workDir, f'Frames (*{" *".join(cryio.extensions())})')[0]
        self.addSubItems(fs, item)

    def addSubItems(self, fs, item):
        item.setExpanded(True)
        if fs:
            fs.sort()
            for f in fs:
                if os.path.exists(f):
                    i = TreeWidgetItem(item)
                    i.setText(0, f)
            self.itemSignals[item].openEmit(fs)

    def itemClicked(self, item, col):
        if col or item in self.itemSignals.keys():
            return

    def loadSetting(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WFTree/Geometry', b''))
        for item in self.itemSignals.keys():
            names = json.loads(s.value(f'WFTree/{item.text(0)}', '[]', str))
            self.addSubItems(names, item)
            item.setCheckState(1, s.value(f'WFTree/{item.text(0)}_checked', QtCore.Qt.Unchecked, int))

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WFTree/Geometry', self.saveGeometry())
        for item in self.itemSignals.keys():
            names = [item.child(i).text(0) for i in range(item.childCount())]
            s.setValue(f'WFTree/{item.text(0)}', json.dumps(names))
            s.setValue(f'WFTree/{item.text(0)}_checked', item.checkState(1))
