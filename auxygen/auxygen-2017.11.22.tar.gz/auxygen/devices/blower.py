#!/usr/bin/python
# -*- coding: utf-8 -*-

from PyQt5 import QtCore
import aspic
from .logger import Logger


class Blower(QtCore.QObject):
    sigTemperature = QtCore.pyqtSignal(float)
    sigError = QtCore.pyqtSignal(str)
    sigConnected = QtCore.pyqtSignal()
    secCounterValue = 0.001

    def __init__(self):
        super().__init__()
        self.logger = Logger('Blower')
        self.temp = 0
        self.target = 0
        self.ramp = 0
        self.ceuro = None
        self.running = False
        self.timer = QtCore.QTimer()
        self.timer.setInterval(1000)
        # noinspection PyUnresolvedReferences
        self.timer.timeout.connect(self.runCounter)

    def runCounter(self):
        self.ceuro.count(self.secCounterValue)

    def setConnected(self):
        if self.ceuro.isConnected():
            self.logger.info('Connected to spec')
            self.timer.start()
            self.running = True
            self.sigConnected.emit()

    def error(self, msg):
        self.logger.error(f'Error: {msg}')
        self.stop()
        self.sigError.emit(msg)

    def checkCounterValue(self, name, value):
        if self.running and name == self.ceuro.name():
            self.temp = value
            self.sigTemperature.emit(self.temp)

    def connectToSpec(self, host, session, counter, cramp, ctarget):
        self.logger.info('Trying connect to spec...')
        self.cramp = cramp
        self.ctarget = ctarget
        self.ceuro = aspic.Qounter((host, session), counter)
        self.ceuro.sigError.connect(self.error)
        self.ceuro.sigConnected.connect(self.setConnected)
        self.ceuro.sigValueChanged.connect(self.checkCounterValue)
        self.cmd = aspic.Qommand(self.ceuro.connection())

    def stop(self):
        self.logger.info('Stopping...')
        self.timer.stop()
        if self.ceuro:
            self.ceuro.sigError.disconnect()
            self.ceuro.sigConnected.disconnect()
            self.ceuro.sigValueChanged.disconnect()
            self.ceuro = None
        self.running = False

    def setRamp(self, value):
        if self.running:
            cmd = self.cramp.format(value)
            self.logger.info(f'Set ramp: {cmd}')
            self.cmd.run(cmd)

    def run(self, target, ramp):
        if self.running:
            self.target = target
            self.ramp = ramp
            self.setRamp(self.ramp)
            self.logger.info(f'Run to {self.target:.2f} with ramp {self.ramp:.2f}')
            self.cmd.run(self.ctarget.format(self.target))

    def pause(self):
        self.logger.info('Pause')
        self.run(self.temp, self.ramp)

    def resume(self):
        self.logger.info('Resume after pause')
        self.run(self.target, self.ramp)
