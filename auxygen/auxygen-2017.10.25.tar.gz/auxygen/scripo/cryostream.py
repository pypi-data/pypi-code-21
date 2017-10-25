#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from .utils import customable


class Cryostream(QtCore.QObject):
    _sigHoldFromSeq = QtCore.pyqtSignal(dict, object)
    _sigCreateSeqAction = QtCore.pyqtSignal(str, float, int, bool)
    _sigCreateSeqWaitAction = QtCore.pyqtSignal(dict, object, bool)
    specialWords = {'cryostream.cool', 'cryostream.ramp', 'cryostream.end', 'cryostream.wait', 'cryostream.purge'}

    def __init__(self):
        super().__init__()
        self._temp = 0

    @customable
    def cool(self, temp, **kwargs):
        temp = float(temp)
        if not 80. <= temp <= 500:
            raise ValueError('The cryostream temperature range is between 80 and 500 K')
        self._sigCreateSeqAction.emit('Cool', temp, 0, kwargs.get('now', False))

    @customable
    def ramp(self, temp, rate, **kwargs):
        temp = float(temp)
        if not 80. <= temp <= 500:
            raise ValueError('The cryostream temperature range is between 80 and 500 K')
        rate = int(rate)
        if not 1 <= rate <= 360:
            raise ValueError('The cryostream rate must be between 1 and 360 K/hour')
        self._sigCreateSeqAction.emit('Ramp', temp, rate, kwargs.get('now', False))

    @customable
    def end(self, **kwargs):
        self._sigCreateSeqAction.emit('End', 0, 360, kwargs.get('now', False))

    @customable
    def wait(self, **kwargs):
        self._sigCreateSeqWaitAction.emit({'Wait for the cryostream hold phase': 'waitOnHold=1'}, self._sigHoldFromSeq,
                                          kwargs.get('now', False))

    def _setTemp(self, status):
        self._temp = status['SampleTemp']

    @property
    def temp(self):
        return self._temp
