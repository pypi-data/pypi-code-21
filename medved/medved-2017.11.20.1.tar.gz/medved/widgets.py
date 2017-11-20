#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtWidgets, QtGui
import qtsnbl.widgets
from .ui.ui_wabout import Ui_WAbout


class ProgressWindow(QtWidgets.QDialog, qtsnbl.widgets.FixedWidget):
    sigCancel = QtCore.pyqtSignal()

    def __init__(self, parent):
        super().__init__(parent)
        self.setupUI()
        self.connectSignals()
        self.fixWindow()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.bb.rejected.connect(self.cancel)

    def setupUI(self):
        self.label = QtWidgets.QLabel()
        self.bb = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Cancel)
        self.pb = QtWidgets.QProgressBar()
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.pb)
        layout.addWidget(self.bb)
        self.setLayout(layout)
        self.setWindowModality(QtCore.Qt.WindowModal)

    def setValue(self, value):
        self.pb.setValue(value)
        if self.pb.maximum() == value:
            self.hide()

    def setMaximum(self, value):
        self.pb.setMaximum(value)

    def setText(self, text):
        self.label.setText(text)

    def showEvent(self, event):
        self.setValue(0)
        super().showEvent(event)

    def cancel(self):
        self.hide()
        self.sigCancel.emit()


class TreeWidget(QtWidgets.QTreeWidget):
    sigItemMoved = QtCore.pyqtSignal(int, int)

    def __init__(self):
        super().__init__()
        # self.setDragAndDrop()

    def setDragAndDrop(self):
        self.oldIndex = None
        self.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.setDragEnabled(True)
        self.viewport().setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QtWidgets.QAbstractItemView.InternalMove)

    def dropEvent(self, event: QtGui.QDropEvent):
        droppedIndex = self.indexAt(event.pos())
        if not droppedIndex.isValid() or not self.oldIndex:
            return
        super().dropEvent(event)
        dp = self.dropIndicatorPosition()
        if dp == QtWidgets.QAbstractItemView.BelowItem and self.oldIndex > droppedIndex:
            droppedIndex = droppedIndex.sibling(droppedIndex.row() + 1, droppedIndex.column())
        elif dp == QtWidgets.QAbstractItemView.AboveItem and self.oldIndex < droppedIndex:
            droppedIndex = droppedIndex.sibling(droppedIndex.row() - 1, droppedIndex.column())
        selectionModel = self.selectionModel()
        selectionModel.clearSelection()
        selectionModel.select(droppedIndex, QtCore.QItemSelectionModel.Select)
        self.sigItemMoved.emit(self.oldIndex.row(), droppedIndex.row())
        self.oldIndex = None

    def dragEnterEvent(self, event: QtGui.QDragEnterEvent):
        oldIndex = self.indexAt(event.pos())
        if oldIndex.isValid():
            super().dragEnterEvent(event)
            self.oldIndex = oldIndex


class WAbout(QtWidgets.QDialog, Ui_WAbout, qtsnbl.widgets.FixedWidget):
    def __init__(self, parent, hg_hash, version):
        super().__init__(parent=parent)
        self.setupUi(self)
        lt = self.aboutLabel.text()
        lt = lt.replace('##', hg_hash).replace('@@', version)
        self.aboutLabel.setText(lt)
        self.fixWindow()

    @QtCore.pyqtSlot()
    def on_closeButton_clicked(self):
        self.close()

    @QtCore.pyqtSlot()
    def on_aboutQtButton_clicked(self):
        QtWidgets.QMessageBox.aboutQt(self)


class CustomImageView(qtsnbl.widgets.ImageView):
    sigX = QtCore.pyqtSignal(int)
    sigY = QtCore.pyqtSignal(int)
    sigBottomAxisRealRangeChanged = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.maxX = self.maxY = self.maxXX = self.maxYY = -1

    def connectSignals(self):
        super().connectSignals()
        self.sigLeftAxisRangeChanged.connect(self.changeDataLeftRange)
        self.sigBottomAxisRangeChanged.connect(self._changeDataBottomRange)

    def changeDataLeftRange(self, mi, ma):
        try:
            self.leftAxis.setRealRange(self.calcY(mi), self.calcY(ma))
        except ZeroDivisionError:
            return

    def _changeDataBottomRange(self, mi, ma):
        try:
            self.sigBottomAxisRealRangeChanged.emit(self.calcX(mi), self.calcX(ma))
        except ZeroDivisionError:
            return

    def changeDataBottomRange(self, mi, ma):
        self.bottomAxis.setRealRange(mi, ma)

    def calcY(self, y=None):
        return self.maxYY - (y or self.y) / self.stepY

    def calcX(self, x=None):
        return (x or self.x) / self.stepX

    def calcROI(self):
        if 0 <= self.y < self.maxY:
            self.sigY.emit(int(self.calcY()))
        if 0 <= self.x < self.maxX:
            self.sigX.emit(int(self.calcX()))

    def setMaxX(self, value):
        self.maxXX = value
        self.maxX = value * self.stepX

    def setMaxY(self, value):
        self.maxYY = value
        self.maxY = value * self.stepY

    def setHLine(self, y):
        self.y = self.maxY - y * self.stepY - self.stepY / 2
        self.hLine.setPos(self.y)
