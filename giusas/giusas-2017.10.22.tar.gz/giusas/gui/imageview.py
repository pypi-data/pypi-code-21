#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from pyqtgraph.graphicsItems.ViewBox import ViewBoxMenu, ViewBox


class CustomViewBoxMenu(ViewBoxMenu.ViewBoxMenu):
    menuPositionSignal = QtCore.pyqtSignal(QtCore.QPoint)

    def __init__(self, view):
        super().__init__(view)
        self.setCustomActions()

    def setCustomActions(self):
        self.addSeparator()
        self.setBeamCenterAction = self.addAction('Set beam center')
        self.setBeamCenterAction.triggered.connect(self.setBeamCenter)

    def setBeamCenter(self):
        self.menuPositionSignal.emit(self.pos())


class CustomViewBox(ViewBox):
    mouseLeftClickedSignal = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.menu = CustomViewBoxMenu(self)
        self.connectSignals()

    def connectSignals(self):
        pass

    def mouseClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouseLeftClickedSignal.emit()
        else:
            ViewBox.mouseClickEvent(self, event)


class AxisItem(pg.AxisItem):
    changeRangeSignal = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        self.range = [0, 1]
        super().__init__(*args, **kwargs)
        self.real_range = [0, 1]

    def setRange(self, mn, mx):
        self.real_range = [mn, mx]
        self.changeRangeSignal.emit(mn, mx)

    def setRealRange(self, mn, mx):
        return super().setRange(mn, mx)

    def changeUnits(self):
        self.setRange(*self.real_range)


class ImageView(pg.GraphicsLayoutWidget):
    CROSS_WIDTH = 2
    CROSS_HEIGHT = 30
    CROSS_HALF = CROSS_HEIGHT / 2 - 1
    setBeamCenterSignal = QtCore.pyqtSignal(float, float)
    setHROIDataSignal = QtCore.pyqtSignal(np.ndarray, np.ndarray, bool, tuple)
    setVROIDataSignal = QtCore.pyqtSignal(np.ndarray, np.ndarray, bool, tuple)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.image = None
        self.vsize = 1
        self.hsize = 1
        self.x = 0
        self.y = 0
        self.view = CustomViewBox()
        self.view.setAspectLocked(True)
        self.view.menu.menuPositionSignal.connect(self.calculateBeamCenter)
        self.view.mouseLeftClickedSignal.connect(self.drawROIcuts)
        # TODO: .addPlot adds a PlotItem, which takes AxisItem parameters
        # TODO: this AxisItems should be considered to show angles from model (or momentum)
        self.leftAxis = AxisItem('left')
        self.bottomAxis = AxisItem('bottom')
        axisItems = {'left': self.leftAxis, 'bottom': self.bottomAxis}
        self.plot2D = self.addPlot(viewBox=self.view, axisItems=axisItems)
        self.imageItem = pg.ImageItem()
        self.plot2D.addItem(self.imageItem)
        self.histogram = pg.HistogramLUTItem()
        self.histogram.setImageItem(self.imageItem)
        self.addItem(self.histogram)
        self.drawCross()
        self.drawCrossHair()

    def setImage(self, image, autoLevels=False, autoRange=False):
        self.image = image
        if self.image is None:
            self.imageItem.clear()
        else:
            self.imageItem.setImage(self.image, autoLevels=autoLevels, autoRange=autoRange)

    def setLevels(self, lmin, lmax):
        self.histogram.setLevels(lmin, lmax)

    def autoLevels(self):
        self.setLevels(0, self.image.mean() + 8 * self.image.std())

    def autoRange(self):
        self.view.autoRange()

    def drawCross(self):
        color = QtGui.QColor(255, 0, 0, 150)
        self.vcross = QtWidgets.QGraphicsRectItem(self.CROSS_HALF, 0, self.CROSS_WIDTH, self.CROSS_HEIGHT)
        self.vcross.setPen(QtGui.QPen(color))
        self.vcross.setBrush(QtGui.QBrush(color))
        self.view.addItem(self.vcross)
        self.hcross = QtWidgets.QGraphicsRectItem(0, self.CROSS_HALF, self.CROSS_HEIGHT, self.CROSS_WIDTH)
        self.hcross.setPen(QtGui.QPen(color))
        self.hcross.setBrush(QtGui.QBrush(color))
        self.view.addItem(self.hcross)
        self.vcross.setVisible(False)
        self.hcross.setVisible(False)

    def calculateBeamCenter(self, menuPos):
        pos = self.view.mapSceneToView(self.mapFromGlobal(menuPos))
        x, y = pos.x() - 0.5, pos.y() - 0.5
        self.drawBeamCenter(x, y)
        self.setBeamCenterSignal.emit(x, y)

    def drawBeamCenter(self, x, y):
        self.hcross.setY(y - self.CROSS_HALF)
        self.hcross.setX(x - self.CROSS_HALF)
        self.vcross.setX(x - self.CROSS_HALF)
        self.vcross.setY(y - self.CROSS_HALF)
        self.vcross.setVisible(True)
        self.hcross.setVisible(True)

    def drawCrossHair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.view.addItem(self.vLine, ignoreBounds=True)
        self.view.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.view.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def mouseMoved(self, event=None):
        if self.image is None:
            return
        self.drawROIcuts(event[0])

    def drawROIcuts(self, pos=None):
        if pos and self.view.sceneBoundingRect().contains(pos):
            mousePoint = self.view.mapSceneToView(pos)
            x, y = mousePoint.x(), mousePoint.y()
            self.vLine.setPos(x)
            self.hLine.setPos(y)
            self.x, self.y = x, y
        else:
            x, y = self.x, self.y
        if x and y:
            (xmin, xmax), (ymin, ymax) = self.view.viewRange()
            hroi = pg.ROI(pos=(xmin, y-self.hsize/2), size=(xmax-xmin, self.hsize), angle=0)
            vroi = pg.ROI(pos=(x-self.vsize/2, ymin), size=(self.vsize, ymax-ymin), angle=0)
            hroi.setVisible(False)
            vroi.setVisible(False)
            self.view.addItem(hroi)
            self.view.addItem(vroi)
            hdata, hcoords = hroi.getArrayRegion(self.image, self.imageItem, returnMappedCoords=True)
            self.setHROIDataSignal.emit(hdata, hcoords, not bool(pos), (x, y))
            vdata, vcoords = vroi.getArrayRegion(self.image, self.imageItem, returnMappedCoords=True)
            self.setVROIDataSignal.emit(vdata, vcoords, not bool(pos), (x, y))
            self.view.removeItem(hroi)
            self.view.removeItem(vroi)

    def changeHCutSize(self, size):
        self.hsize = size

    def changeVCutSize(self, size):
        self.vsize = size
