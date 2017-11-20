#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
from PyQt5 import QtCore, QtGui, QtWidgets
import pyqtgraph as pg
from .axisitem import AxisItem
from .viewbox import ViewBox


class ImageView(pg.GraphicsLayoutWidget):
    sigHROIData = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sigVROIData = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sigHCutValues = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sigVCutValues = QtCore.pyqtSignal(np.ndarray, np.ndarray)
    sigMouseLeftClicked = QtCore.pyqtSignal(float, float)
    sigLeftAxisRangeChanged = QtCore.pyqtSignal(float, float)
    sigBottomAxisRangeChanged = QtCore.pyqtSignal(float, float)

    def __init__(self, parent=None, **kwargs):
        super().__init__(parent, **kwargs)
        self.move_cross = True
        self.image = None
        self.smooth = True
        self.old_image = None
        self.vsize = 1
        self.hsize = 1
        self.x = 0
        self.y = 0
        self.stepY = 0
        self.stepX = 0
        self.view = ViewBox()
        self.view.setAspectLocked(True)
        # TODO: .addPlot adds a PlotItem, which takes AxisItem parameters
        # TODO: this AxisItems should be considered to show angles from model (or momentum)
        self.leftAxis = AxisItem('left')
        self.bottomAxis = AxisItem('bottom')
        self.leftAxis.linkToView(self.view)
        self.bottomAxis.linkToView(self.view)
        axisItems = {'left': self.leftAxis, 'bottom': self.bottomAxis}
        self.plot2D = self.addPlot(viewBox=self.view, axisItems=axisItems)
        self.imageItem = pg.ImageItem()
        self.plot2D.addItem(self.imageItem)
        self.histogram = pg.HistogramLUTItem()
        self.histogram.setImageItem(self.imageItem)
        self.addItem(self.histogram)
        color = QtGui.QColor(255, 0, 0, 150)
        self.areaX = QtWidgets.QGraphicsRectItem(0, 0, 1, 1)
        self.areaX.setPen(QtGui.QPen(color))
        self.areaX.setBrush(QtGui.QBrush(color))
        self.areaY = QtWidgets.QGraphicsRectItem(0, 0, 1, 1)
        self.areaY.setPen(QtGui.QPen(color))
        self.areaY.setBrush(QtGui.QBrush(color))
        self.areaX.setVisible(False)
        self.areaY.setVisible(False)
        self.view.addItem(self.areaX)
        self.view.addItem(self.areaY)
        self.drawCrossHair()
        self.connectSignals()

    def connectSignals(self):
        self.sigHROIData.connect(self.calcHCut)
        self.sigVROIData.connect(self.calcVCut)
        self.view.sigMouseLeftClick.connect(lambda: self.sigMouseLeftClicked.emit(self.x, self.y))
        self.leftAxis.sigChangeRange.connect(self.sigLeftAxisRangeChanged.emit)
        self.bottomAxis.sigChangeRange.connect(self.sigBottomAxisRangeChanged.emit)

    def setImage(self, image, autoLevels=False, autoRange=False):
        self.image = image
        if self.image is None:
            self.imageItem.clear()
        else:
            self.imageItem.setImage(self.image, autoLevels=autoLevels, autoRange=autoRange)

    def setLevels(self, lmin, lmax):
        self.histogram.setLevels(lmin, lmax)

    def autoLevels(self, method='mean'):
        if method == 'mean':
            self.setLevels(0, self.image.mean() + 8 * self.image.std())
        elif method == 'max':
            levelMax = self.quickMinMax(self.image)[1]
            self.setLevels(-levelMax / 20, levelMax / 4)

    def autoRange(self):
        self.view.autoRange()

    def drawCrossHair(self):
        self.vLine = pg.InfiniteLine(angle=90, movable=False)
        self.hLine = pg.InfiniteLine(angle=0, movable=False)
        self.view.addItem(self.vLine, ignoreBounds=True)
        self.view.addItem(self.hLine, ignoreBounds=True)
        self.proxy = pg.SignalProxy(self.view.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

    def mouseMoved(self, event=None):
        if self.image is None or event is None or not self.move_cross:
            return
        self.drawROI(event[0])
        self.calcROI()

    def drawROI(self, pos):
        if self.view.sceneBoundingRect().contains(pos):
            mousePoint = self.view.mapSceneToView(pos)
            self.x, self.y = mousePoint.x(), mousePoint.y()
            self.vLine.setPos(self.x)
            self.hLine.setPos(self.y)

    def calcROI(self):
        (xmin, xmax), (ymin, ymax) = self.view.viewRange()
        hpos = xmin, self.y - self.hsize / 2
        hsize = xmax - xmin, self.hsize
        vpos = self.x - self.vsize / 2, ymin
        vsize = self.vsize, ymax - ymin
        if not self.smooth:
            hpos, hsize, vpos, vsize = map(np.rint, (hpos, hsize, vpos, vsize))
        self.sigHROIData.emit(*self.getROIData(hpos, hsize))
        self.sigVROIData.emit(*self.getROIData(vpos, vsize))

    def getROIData(self, pos, size):
        roi = pg.ROI(pos=pos, size=size, angle=0)
        roi.setVisible(False)
        self.view.addItem(roi)
        # we don't want to calc a cut if the log mode is on
        image = self.image if self.old_image is None else self.old_image
        data, coords = roi.getArrayRegion(image, self.imageItem, returnMappedCoords=True)
        self.view.removeItem(roi)
        return data, coords

    def calcHCoords(self, data, coords):
        if data is None:
            return
        while data.ndim > 1:
            data = data.mean(axis=1)
        while coords.ndim > 2:
            coords = coords[:, :, 0]
        hcd = coords - coords[:, 0, np.newaxis]
        x = np.sqrt((hcd ** 2).sum(axis=0)) + coords[0][0]
        return x, data

    def calcHCut(self, data, coords):
        try:
            x, data = self.calcHCoords(data, coords)
        except IndexError:
            return
        self.sigHCutValues.emit(x, data)

    def calcVCoords(self, data, coords):
        if data is None:
            return
        while data.ndim > 1:
            data = data.mean(axis=0)
        while coords.ndim > 2:
            coords = coords[:, 0, :]
        hcd = coords - coords[:, 0, np.newaxis]
        y = np.sqrt((hcd ** 2).sum(axis=0)) + coords[1][0]
        return y, data

    def calcVCut(self, data, coords):
        try:
            y, data = self.calcVCoords(data, coords)
        except IndexError:
            return
        self.sigVCutValues.emit(y, data)

    def rotateImage(self):
        if self.image is None:
            return
        self.setImage(np.rot90(self.image, 3))

    def flipHImage(self):
        if self.image is None:
            return
        self.setImage(np.flipud(self.image))

    def flipVImage(self):
        if self.image is None:
            return
        self.setImage(np.fliplr(self.image))

    def logImage(self, on: bool):
        if self.image is None:
            return
        if on:
            self.old_image = self.image
            # there is no point to log array values which are less than 1
            # it results in NaNs and zero divisions, too bad
            self.setImage(np.log(np.where(self.image > 1, self.image, np.ones_like(self.image))), True, True)
        else:
            image = self.old_image
            self.old_image = None
            self.setImage(image, True)

    def setSmooth(self, smooth):
        self.smooth = smooth

    def rescaleImage(self):
        if self.image is None:
            return
        viewRect = self.view.rect()
        self.imageItem.setRect(viewRect)
        self.view.autoRange()
        width, height = viewRect.width(), viewRect.height()
        self.stepY = height / self.imageItem.height()
        self.stepX = width / self.imageItem.width()
        self.areaY.setRect(0, self.stepY, width, self.stepY + 1)
        self.areaX.setRect(self.stepX, 0, self.stepX + 1, height)

    def quickMinMax(self, data):
        """
        Estimate the min/max values of *data* by subsampling.
        """
        while data.size > 1e6:
            ax = np.argmax(data.shape)
            sl = [slice(None)] * data.ndim
            sl[ax] = slice(None, None, 2)
            data = data[sl]
        return np.nanmin(data), np.nanmax(data)

    def moveCross(self):
        self.move_cross = True

    def fixCross(self):
        self.move_cross = False
