#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .utils import customable


class Blower(QtCore.QObject):
    _sigWaitFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCreateBlowerAction = QtCore.pyqtSignal(float, float, bool)
    _sigCreateBlowerWaitAction = QtCore.pyqtSignal(dict, object, bool)
    specialWords = {'blower.ramp', 'blower.wait', 'blower.temp'}

    def __init__(self):
        super().__init__()
        self._temp = 0

    @customable
    def ramp(self, temp, rate, **kwargs):
        if not 25 <= temp <= 1000:
            raise ValueError('The Eurotherm temperature must be between 25 and 1000 C')
        if not 0 <= rate <= 1000:
            raise ValueError('The Eurotherm ramp rate must be between 0 and 1000 C/min')
        self._sigCreateBlowerAction.emit(temp, rate, kwargs.get('now', False))

    @customable
    def wait(self, **kwargs):
        self._sigCreateBlowerWaitAction.emit({'Wait for the Eurotherm temperature': 'waitOnTemp=1'},
                                             self._sigWaitFromSeq, kwargs.get('now', False))

    def _setTemp(self, temp):
        self._temp = temp

    @property
    def temp(self):
        return self._temp
