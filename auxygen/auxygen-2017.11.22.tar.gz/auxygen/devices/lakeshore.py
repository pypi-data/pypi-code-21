#!/usr/bin/python
# -*- coding: utf-8 -*-

import collections
from PyQt5 import QtCore, QtNetwork


class Lakeshore(QtCore.QObject):
    sigConnected = QtCore.pyqtSignal()
    sigDisconnected = QtCore.pyqtSignal()
    sigTemperature = QtCore.pyqtSignal(str, float)
    sigHeater = QtCore.pyqtSignal(int, float)
    sigRange = QtCore.pyqtSignal(int, int)
    sigPID = QtCore.pyqtSignal(int, float, float, float)
    sigMout = QtCore.pyqtSignal(int, float)
    sigSetpoint = QtCore.pyqtSignal(int, float)
    sigError = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.timerSend = QtCore.QTimer(self)
        self.timerSend.setInterval(10)
        self.timerPoll = QtCore.QTimer(self)
        self.timerPoll.setInterval(1000)
        self.socket = QtNetwork.QTcpSocket(self)
        self.socket.setProxy(QtNetwork.QNetworkProxy(QtNetwork.QNetworkProxy.NoProxy))
        self.queue = collections.deque()
        self.readA = False
        self.readB = False
        self.readC = False
        self.readD = False
        self.read1 = False
        self.read2 = False
        self.connectSignals()

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.timerPoll.timeout.connect(self.poll)
        self.timerSend.timeout.connect(self._send)
        self.socket.connected.connect(self.sendFirstRequest)
        self.socket.readyRead.connect(self.readResponse)
        self.socket.disconnected.connect(self.stop)
        self.socket.error.connect(self.serverHasError)

    def start(self, host, port):
        self.callback = None
        self.queue.clear()
        self.socket.connectToHost(host, port)

    def sendFirstRequest(self):
        self.timerPoll.start()
        self.timerSend.start()
        self.sigConnected.emit()

    def readResponse(self):
        response = bytes(self.socket.readAll()).decode(errors='ignore')
        if self.callback is not None:
            callback = self.callback
            self.callback = None
            callback(response)

    def serverHasError(self):
        msg = self.socket.errorString()
        self.sigError.emit(f'Cannot connect to Lakeshore:\n{msg}')
        self.stop()

    def stop(self):
        if self.timerPoll.isActive():
            self.timerPoll.stop()
            self.timerSend.stop()
            self.socket.disconnectFromHost()
        self.sigDisconnected.emit()

    def send(self, cmd, callback=None):
        self.queue.append((cmd, callback))

    def _send(self):
        if self.queue and not self.callback:
            cmd, self.callback = self.queue.popleft()
            self.socket.write(f'{cmd}\r\n'.encode())

    def poll(self):
        self.getTemp()
        self.getHeater()
        self.getRange()
        self.getPID()
        self.getMout()
        self.getSetP()

    def getRange(self):
        if self.read1:
            self.send(f'RANGE? 1', lambda v: self.sigRange.emit(1, float(v)))
        if self.read2:
            self.send(f'RANGE? 2', lambda v: self.sigRange.emit(2, float(v)))

    def setRange(self, output, value):
        self.send(f'RANGE {output},{value:.2f}')

    def getTemp(self):
        if self.readA:
            self.send('KRDG? A', lambda v: self.sigTemperature.emit('A', float(v)))
        if self.readB:
            self.send('KRDG? B', lambda v: self.sigTemperature.emit('B', float(v)))
        if self.readC:
            self.send('KRDG? C', lambda v: self.sigTemperature.emit('C', float(v)))
        if self.readD:
            self.send('KRDG? D', lambda v: self.sigTemperature.emit('D', float(v)))

    def getHeater(self):
        if self.read1:
            self.send(f'HTR? 1', lambda v: self.sigHeater.emit(1, float(v)))
        if self.read2:
            self.send(f'HTR? 2', lambda v: self.sigHeater.emit(2, float(v)))

    def getMout(self):
        if self.read1:
            self.send(f'MOUT? 1', lambda v: self.sigMout.emit(1, float(v)))
        if self.read2:
            self.send(f'MOUT? 2', lambda v: self.sigMout.emit(2, float(v)))

    def setMout(self, output, value):
        self.send(f'MOUT {output},{value:.2f}')

    def getPID(self):
        if self.read1:
            self.send(f'PID? 1', lambda v: self.sigPID.emit(1, *map(float, v.split(','))))
        if self.read2:
            self.send(f'PID? 2', lambda v: self.sigPID.emit(2, *map(float, v.split(','))))

    def setPID(self, output, pid):
        pid = pid.split()
        if len(pid) >= 3:
            p, i, d = pid[:3]
        elif len(pid) == 2:
            p, i, d = pid[0], pid[1], 0
        elif len(pid) == 1:
            p, i, d = pid[0], 0, 0
        else:
            return
        self.send(f'PID {output},{p},{i},{d}')

    def getSetP(self):
        if self.read1:
            self.send(f'SETP? 1', lambda v: self.sigSetpoint.emit(1, float(v)))
        if self.read2:
            self.send(f'SETP? 2', lambda v: self.sigSetpoint.emit(2, float(v)))

    def setSetP(self, output, value):
        self.send(f'SETP {output},{value:.2f}')

    def setReadOutputAndSensor(self, value, read):
        setattr(self, f'read{value}', read)
