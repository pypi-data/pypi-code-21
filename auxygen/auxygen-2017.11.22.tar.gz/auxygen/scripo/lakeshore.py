#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from ..gui.wlakeshore import WLakeshore
from .utils import customable


class Lakeshore(QtCore.QObject):
    _sigSetPoint = QtCore.pyqtSignal(int, float, bool)
    _sigSetRange = QtCore.pyqtSignal(int, int, bool)
    _sigSetManual = QtCore.pyqtSignal(int, float, bool)
    _sigSetPID = QtCore.pyqtSignal(int, float, float, float, bool)
    _sigHoldFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    specialWords = {'lakeshore.setpoint', 'lakeshore.pid', 'lakeshore.manual', 'lakeshore.range', 'lakeshore.wait'}

    def __init__(self):
        super().__init__()

    @customable
    def pid(self, output, p, i, d, **kwargs):
        if not 0 < output < 3:
            raise ValueError('The lakeshore output should be 1 or 2')
        if not 0 <= p <= 1000:
            raise ValueError('The Lakeshore propotional value must be between 0.1 and 1000')
        if not 0 <= i <= 1000:
            raise ValueError('The Lakeshore integral value must be between 0.1 and 1000')
        if not 0 <= d <= 200:
            raise ValueError('The Lakeshore differential value must be between 0.1 and 200')
        self._sigSetPID.emit(output, p, i, d, kwargs.get('now', False))

    @customable
    def range(self, output, value, **kwargs):
        if isinstance(value, str):
            try:
                value = WLakeshore.HeaterRange.index(value)
            except (ValueError, IndexError):
                value = -1
        if not 0 <= value <= 3:
            raise ValueError('The Lakeshore range should be int [0; 3] or string ["Off", "Low", ...]')
        self._sigSetRange.emit(output, value, kwargs.get('now', False))

    @customable
    def manual(self, output, value, **kwargs):
        if not 0 < output < 3:
            raise ValueError('The lakeshore output should be 1 or 2')
        if not 0 <= value <= 100:
            raise ValueError('The Lakeshore manual output value must be between 0 and 100')
        self._sigSetManual.emit(output, value, kwargs.get('now', False))

    @customable
    def setpoint(self, output, value, **kwargs):
        if not 0 < output < 3:
            raise ValueError('The lakeshore output should be 1 or 2')
        if not 0 <= value <= 1000:
            raise ValueError('The Lakeshore setp value must be between 0 and 1000 K')
        self._sigSetPoint.emit(output, value, kwargs.get('now', False))

    @customable
    def wait(self, **kwargs):
        self._sigCreateSeqAction.emit({'Wait for the Lakeshore temperature': 'waitOnTemp=1'}, self._sigHoldFromSeq,
                                      kwargs.get('now', False))
