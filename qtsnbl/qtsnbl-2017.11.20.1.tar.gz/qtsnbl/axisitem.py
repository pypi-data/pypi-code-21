#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import pyqtgraph as pg


class AxisItem(pg.AxisItem):
    sigChangeRange = QtCore.pyqtSignal(float, float)

    def __init__(self, *args, **kwargs):
        self.range = [0, 1]
        super().__init__(*args, **kwargs)
        self.real_range = [0, 1]

    def setRange(self, mn, mx):
        self.real_range = [mn, mx]
        self.sigChangeRange.emit(mn, mx)

    def setRealRange(self, mn, mx):
        return super().setRange(mn, mx)

    def changeUnits(self):
        self.setRange(*self.real_range)
