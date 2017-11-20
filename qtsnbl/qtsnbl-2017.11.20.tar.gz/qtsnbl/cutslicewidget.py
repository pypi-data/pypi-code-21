#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtWidgets, QtGui
import numpy as np
import pyqtgraph as pg
from pyqtgraph import dockarea
from .imageview import ImageView


class CutSliceWidget(QtWidgets.QWidget):
    SizeX = 1600
    SizeY = 1200
    Size1D = 200
    sig2DMouseLeftClicked = QtCore.pyqtSignal(float, float)
    sigXMouseMoved = QtCore.pyqtSignal(float, float)
    sigYMouseMoved = QtCore.pyqtSignal(float, float)

    def __init__(self, parent=None, *, imageview=None):
        super().__init__(parent)
        self.resize(self.SizeX, self.SizeY)
        self.plot2DView = imageview or ImageView()
        self.setActions()
        self.setUI()
        self.connectSignals()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.actionAdjustLevels.triggered.connect(self.adjustImageLevels)
        self.actionRotateImage.triggered.connect(self.plot2DView.rotateImage)
        self.actionFlipImageH.triggered.connect(self.plot2DView.flipHImage)
        self.actionFlipImageV.triggered.connect(self.plot2DView.flipVImage)
        self.actionLogarithmicScale.triggered.connect(self.plot2DView.logImage)
        self.plot2DView.sigHCutValues.connect(self.plotHCut)
        self.plot2DView.sigVCutValues.connect(self.plotVCut)
        self.plot2DView.sigMouseLeftClicked.connect(self.sig2DMouseLeftClicked.emit)

    def setActions(self):
        self.actionRotateImage = QtWidgets.QAction(self)
        self.actionRotateImage.setIcon(QtGui.QIcon(':/rotate'))
        self.actionRotateImage.setText('Rotate image clockwise')
        self.actionRotateImage.setToolTip('Rotate image clockwise')
        self.actionRotateImage.setShortcut('Ctrl+R')
        self.actionFlipImageH = QtWidgets.QAction(self)
        self.actionFlipImageH.setIcon(QtGui.QIcon(':/flip-horizontal'))
        self.actionFlipImageH.setText('Flip image horizontally')
        self.actionFlipImageH.setToolTip('Flip image horizontally')
        self.actionFlipImageH.setShortcut('Ctrl+H')
        self.actionFlipImageV = QtWidgets.QAction(self)
        self.actionFlipImageV.setIcon(QtGui.QIcon(':/flip-vertical'))
        self.actionFlipImageV.setText('Flip image vertically')
        self.actionFlipImageV.setToolTip('Flip image vertically')
        self.actionFlipImageV.setShortcut('Ctrl+V')
        self.actionAdjustLevels = QtWidgets.QAction(self)
        self.actionAdjustLevels.setIcon(QtGui.QIcon(':/adjust'))
        self.actionAdjustLevels.setText('Adjust image levels')
        self.actionAdjustLevels.setToolTip('Adjust image levels')
        self.actionAdjustLevels.setShortcut('Ctrl+A')
        self.actionLogarithmicScale = QtWidgets.QAction(self)
        self.actionLogarithmicScale.setCheckable(True)
        self.actionLogarithmicScale.setIcon(QtGui.QIcon(':/exp'))
        self.actionLogarithmicScale.setText('Set logarithmic scale')
        self.actionLogarithmicScale.setToolTip('Set logarithmic scale')
        self.actionLogarithmicScale.setShortcut('Ctrl+L')

    def setUI(self):
        self.docks = dockarea.DockArea()
        self.dock2D = dockarea.Dock('2D', size=(self.SizeX-self.Size1D, self.SizeY-self.Size1D))
        self.dockx = dockarea.Dock('x', size=(self.SizeX, self.Size1D))
        self.docky = dockarea.Dock('y', size=(self.Size1D, self.SizeY))
        self.docks.addDock(self.dock2D, 'left')
        self.docks.addDock(self.dockx, 'bottom', self.dock2D)
        self.docks.addDock(self.docky, 'right', self.dock2D)
        self.toolbar2D = QtWidgets.QToolBar(self.dock2D)
        self.toolbar2D.addActions([w for a, w in self.__dict__.items() if a.startswith('action')])
        self.dock2D.addWidget(self.toolbar2D)
        self.dock2D.addWidget(self.plot2DView)
        self.plotx = pg.PlotWidget(self.dockx)
        self.hroi = self.plotx.plot()
        self.dockx.addWidget(self.plotx)
        self.ploty = pg.PlotWidget(self.docky)
        self.vroi = self.ploty.plot()
        self.docky.addWidget(self.ploty)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.docks)
        self.setLayout(layout)
        xi = self.plotx.plotItem
        yi = self.ploty.plotItem
        self.proxyx = pg.SignalProxy(xi.scene().sigMouseMoved, rateLimit=60,
                                     slot=lambda e: self.mouseMoved1D(xi, e[0], self.sigXMouseMoved))
        self.proxyy = pg.SignalProxy(yi.scene().sigMouseMoved, rateLimit=60,
                                     slot=lambda e: self.mouseMoved1D(yi, e[0], self.sigYMouseMoved))

    def mouseMoved1D(self, plotItem, pos, signal):
        if plotItem.sceneBoundingRect().contains(pos):
            mousePoint = plotItem.vb.mapSceneToView(pos)
            signal.emit(mousePoint.x(), mousePoint.y())

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue('CutSliceWidget/dockState', json.dumps(self.docks.saveState()))

    def loadSettings(self):
        s = QtCore.QSettings()
        dockState = s.value('CutSliceWidget/dockState', '', str)
        if dockState:
            # noinspection PyBroadException
            try:
                self.docks.restoreState(json.loads(dockState))
            except Exception:  # stupid!
                pass

    def showImage(self, array, adjust=False):
        adjust = adjust or self.plot2DView.image is None
        self.plot2DView.setImage(array, autoLevels=False, autoRange=False)
        if adjust:
            self.actionAdjustLevels.activate(QtWidgets.QAction.Trigger)

    def adjustImageLevels(self):
        if self.plot2DView.image is not None:
            self.plot2DView.autoRange()
            self.plot2DView.autoLevels()

    def plotHCut(self, x: np.ndarray, y: np.ndarray, **kwargs):
        self.hroi.setData(x, y, **kwargs)

    def plotVCut(self, x: np.ndarray, y: np.ndarray, **kwargs):
        self.vroi.setData(y, x, **kwargs)

    def setHCutSize(self, size):
        self.plot2DView.hsize = size

    def setVCutSize(self, size):
        self.plot2DView.vsize = size

    def setSmooth(self, smooth):
        self.plot2DView.setSmooth(smooth)

    def moveCross(self):
        self.plot2DView.moveCross()

    def fixCross(self):
        self.plot2DView.fixCross()

    def clear(self):
        self.plot2DView.setImage(None)
        self.ploty.plotItem.clear()
        self.plotx.plotItem.clear()
