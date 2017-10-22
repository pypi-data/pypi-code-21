#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import dockarea
from .ui.wgiusas import Ui_WGiuSAS
from .imageview import ImageView


class WGiuSAS(QtWidgets.QMainWindow, Ui_WGiuSAS):
    closeEventSignal = QtCore.pyqtSignal()

    def __init__(self, wparams, wftree):
        super().__init__()
        self.wparams = wparams
        self.wftree = wftree
        self.setUI()

    def setUI(self):
        self.setupUi(self)
        self.docks = dockarea.DockArea()
        self.setCentralWidget(self.docks)
        dock2D = dockarea.Dock('2D')
        self.dockqy = dockarea.Dock('qy')
        self.dockqz = dockarea.Dock('qz')
        self.docks.addDock(dock2D, 'left')
        self.docks.addDock(self.dockqy, 'bottom', dock2D)
        self.docks.addDock(self.dockqz, 'right', dock2D)
        self.toolbar2D = QtWidgets.QToolBar(dock2D)
        self.toolbar2D.addActions(
            (self.actionAdjustLevels, self.actionRotateImage, self.actionFlipImageH, self.actionFlipImageV,
             self.actionLogarithmicScale))
        self.plot2DView = ImageView()
        dock2D.addWidget(self.toolbar2D)
        dock2D.addWidget(self.plot2DView)
        self.plotqy = pg.PlotWidget(self.dockqy)
        self.hroi = self.plotqy.plot()
        self.dockqy.addWidget(self.plotqy)
        self.plotqz = pg.PlotWidget(self.dockqz)
        self.vroi = self.plotqz.plot()
        self.dockqz.addWidget(self.plotqz)
        self.dockParams.setWidget(self.wparams)
        self.dockFiles.setWidget(self.wftree)

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('WGiuSAS/Geometry', self.saveGeometry())
        s.setValue('WGiuSAS/State', self.saveState())
        self.dockqz.label.setText('qz')
        self.dockqy.label.setText('qy')
        s.setValue('WGiuSAS/dockState', json.dumps(self.docks.saveState()))
        s.setValue('WGiuSAS/version', 1)

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value('WGiuSAS/Geometry', b''))
        self.restoreState(s.value('WGiuSAS/State', b''))
        version = s.value('WGiuSAS/version', 0, int)
        if version < 1:
            return
        dockState = s.value('WGiuSAS/dockState', '', str)
        if dockState:
            # noinspection PyBroadException
            try:
                self.docks.restoreState(json.loads(dockState))
            except Exception:  # stupid!
                pass

    def closeEvent(self, event):
        self.closeEventSignal.emit()
        event.accept()
        super(WGiuSAS, self).closeEvent(event)

    def show2d(self, array):
        adjust = self.plot2DView.image is None
        self.plot2DView.setImage(array, autoLevels=False, autoRange=False)
        if adjust:
            self.on_actionAdjustLevels_triggered()

    def showError(self, msg):
        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
        QtWidgets.QMessageBox.critical(self, 'GiuSAS error', msg)

    @QtCore.pyqtSlot()
    def on_actionAdjustLevels_triggered(self):
        if self.plot2DView.image is not None:
            self.plot2DView.autoRange()
            self.plot2DView.autoLevels()

    def plotHROIData(self, x, y):
        self.hroi.setData(x, y)

    def plotVROIData(self, x, y):
        self.vroi.setData(y, x)

    def changeCutUnits(self, bottom, right):
        self.dockqy.label.setText(bottom)
        self.dockqz.label.setText(right)

    @QtCore.pyqtSlot()
    def on_actionQuit_triggered(self):
        self.close()

    @QtCore.pyqtSlot(bool)
    def on_actionFiles_toggled(self, checked):
        self.dockFiles.setVisible(checked)

    def on_dockFiles_visibilityChanged(self, visible):
        self.actionFiles.setChecked(visible)

    @QtCore.pyqtSlot(bool)
    def on_actionParameters_toggled(self, checked):
        self.dockParams.setVisible(checked)

    def on_dockParams_visibilityChanged(self, visible):
        self.actionParameters.setChecked(visible)
