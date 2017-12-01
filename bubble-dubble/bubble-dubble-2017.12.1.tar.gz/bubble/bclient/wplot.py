#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
from PyQt5 import QtCore, QtWidgets
import pyqtgraph as pg
from pyqtgraph import dockarea


class WPlot(QtWidgets.QDialog):
    sigClosed = QtCore.pyqtSignal()

    def __init__(self, name, parent=None):
        super().__init__(parent=parent)
        self.data = None
        self.array = None
        self.name = name
        self.title = ''
        self.setupUI()
        self.setWindowTitle(f'{name} plot')

    def setupUI(self):
        self.area = dockarea.DockArea()
        d1 = dockarea.Dock('2D')
        d2 = dockarea.Dock('1D')
        self.area.addDock(d1, 'top')
        self.area.addDock(d2, 'bottom')
        self.plot2DView = pg.ImageView()
        self.plot1DView = pg.PlotWidget()
        d1.addWidget(self.plot2DView)
        d2.addWidget(self.plot1DView)
        self.plotItem = self.plot1DView.getPlotItem()
        self.imageItem = self.plot2DView.getImageItem()
        self.imageView = self.plot2DView.getView()
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.plotItem.vb.addItem(self.vLine, ignoreBounds=True)
        self.plotItem.vb.addItem(self.hLine, ignoreBounds=True)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.area)
        self.setLayout(layout)
        self.proxy1D = pg.SignalProxy(self.plotItem.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved1D)

    def mouseMoved1D(self, evt):
        pos = evt[0]
        if self.plotItem.sceneBoundingRect().contains(pos):
            mousePoint = self.plotItem.vb.mapSceneToView(pos)
            x, y = mousePoint.x(), mousePoint.y()
            self.vLine.setPos(x)
            self.hLine.setPos(y)
            if self.data is None:
                return
            index = int(x)
            if 0 < index < len(self.data):
                self.plot1DView.setTitle(f'{self.title}; x={x:0.3f}, y={self.data[index]:0.3f}')

    def closeEvent(self, event):
        self.sigClosed.emit()

    def saveSettings(self):
        s = QtCore.QSettings()
        s.setValue(f'WPlot{self.name}/Geometry', self.saveGeometry())
        s.setValue(f'WPlot{self.name}/dockState', json.dumps(self.area.saveState()))

    def loadSettings(self):
        s = QtCore.QSettings()
        self.restoreGeometry(s.value(f'WPlot{self.name}/Geometry', b''))
        dockState = s.value(f'WPlot{self.name}/dockState', '', str)
        if dockState:
            # noinspection PyBroadException
            try:
                self.area.restoreState(json.loads(dockState))
            except Exception:
                pass

    def plot(self, response):
        data1d = response.get('data1d', None)
        if data1d:
            x, y, e = data1d
            try:
                y[y <= 0] = y[y > 0].min()
            except ValueError:  # it seems that the array is zero-like, skip it
                pass
            self.data = y
            self.plot1DView.plot(x, y, pen='g', clear=True)
            self.title = f'{response.get("chiFile", "")}; Tr = {response.get("transmission", 0):.5f}'
            self.plot1DView.setTitle(self.title)
        image = response.get('image', None)
        if image is not None:
            self.array = image
            self.plot2DView.setImage(self.array)
            self.plot2DView.setLevels(0, self.array.mean() + 8 * self.array.std())
