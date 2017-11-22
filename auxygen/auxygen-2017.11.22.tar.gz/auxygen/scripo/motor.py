#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
from ..utils import split_motor_name
from .utils import customable


class _Motor(QtCore.QObject):
    _sigMove = QtCore.pyqtSignal(dict, object)
    _sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    _sigMoveFromSeq = QtCore.pyqtSignal(str, float)
    _sigMoveRelFromSeq = QtCore.pyqtSignal(str, float)
    _sigSetSlewRate = QtCore.pyqtSignal(str, float)

    def __init__(self, name):
        super().__init__()
        self.__name = name
        self.__step_size = 0
        self.__max_velocity = 0
        self._sigMove.connect(self.__motorMoveFromSeq)

    @customable
    def move(self, pos, **kwargs):
        self._sigCreateSeqAction.emit({f'Move motor {self.__name} absolutely to {pos}': f'{self.__name}:{pos}:a'},
                                      self._sigMove, kwargs.get('now', False))

    @customable
    def moveRelative(self, pos, **kwargs):
        self._sigCreateSeqAction.emit({f'Move motor {self.__name} relatively to {pos}': f'{self.__name}:{pos}:r'},
                                      self._sigMove, kwargs.get('now', False))

    def __motorMoveFromSeq(self, action, signal):
        if signal:
            name, position, how = list(action.values())[0].split(':')
            if how == 'a':
                self._sigMoveFromSeq.emit(name, float(position))
            elif how == 'r':
                self._sigMoveRelFromSeq.emit(name, float(position))
            signal.emit()

    def wait(self):
        pass

    def name(self):
        return self.__name

    def _setStepSize(self, step_size):
        self.__step_size = step_size

    @customable
    def setSlewRate(self, step, time):
        if self.__max_velocity <= 0:
            raise ValueError(f'Max velocity for {self.__name} is unknown. Please ask you know who')
        velocity = self.__step_size * step / time
        if velocity > self.__max_velocity * self.__step_size:
            raise ValueError(f'Velocity for {self.__name} is too big. Please, increase time')

    @customable
    def setMaxSlewRate(self):
        if self.__max_velocity <= 0:
            raise ValueError(f'Max velocity for {self.__name} is unknown. Please ask you know who')


class Motor(QtCore.QObject):
    _sigCreateSeqAction = QtCore.pyqtSignal(dict, object, bool)
    _sigMoveFromSeq = QtCore.pyqtSignal(str, float)
    _sigMoveRelFromSeq = QtCore.pyqtSignal(str, float)
    __sigWaitFromSeq = QtCore.pyqtSignal(dict, object)
    _sigDiffWait = QtCore.pyqtSignal()
    specialWords = {'motor("").move', 'motor("").moveRelative', 'motor.wait'}

    def __init__(self):
        super().__init__()
        self.__motors = {}
        self.__waitSignal = None
        self.__sigWaitFromSeq.connect(self.__motorWaitFromSeq)

    @split_motor_name
    def _removeMotor(self, motor):
        if '->' in motor:
            motor = motor.split('->')[-1]
        if motor in self.__motors:
            del self.__motors[motor]

    def _addMotors(self, motors):
        for m in motors:
            self._addMotor(m)

    @split_motor_name
    def _addMotor(self, motor):
        if motor not in self.__motors:
            m = _Motor(motor)
            m._sigMoveFromSeq.connect(self._sigMoveFromSeq.emit)
            m._sigMoveRelFromSeq.connect(self._sigMoveRelFromSeq.emit)
            m._sigCreateSeqAction.connect(self._sigCreateSeqAction.emit)
            self.__motors[motor] = m

    def __call__(self, name):
        if name not in self.__motors:
            raise ValueError(f'The motor "{name}" is not connected.')
        return self.__motors[name]

    @customable
    def wait(self, **kwargs):
        return self._wait(**kwargs)

    def _wait(self, **kwargs):
        self._sigCreateSeqAction.emit(
            {'Wait while motors are moving': 'wait=1'},
            self.__sigWaitFromSeq,
            kwargs.get('now', False)
        )

    def __motorWaitFromSeq(self, action, signal):
        if signal:
            self.__action = action
            self.__waitSignal = signal
            self._sigDiffWait.emit()

    def _allMotorsStopped(self):
        if self.__waitSignal:
            self.__waitSignal.emit()
            self.__waitSignal = None

    def _setStepSize(self, name, step_size):
        for m in self.__motors:
            if m == name:
                self.__motors[m]._setStepSize(step_size)
                return
