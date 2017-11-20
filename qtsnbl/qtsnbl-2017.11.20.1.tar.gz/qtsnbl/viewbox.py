#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import pyqtgraph as pg


class ViewBox(pg.ViewBox):
    sigMouseLeftClick = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.connectSignals()

    def connectSignals(self):
        pass

    def mouseClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.sigMouseLeftClick.emit()
        else:
            super().mouseClickEvent(event)
