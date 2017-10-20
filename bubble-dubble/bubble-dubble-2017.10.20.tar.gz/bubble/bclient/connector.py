#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import json
import pickle
import struct
import time
import cryio
import decor
import numpy as np
from PyQt5 import QtCore, QtNetwork
from ..bcommon import compressor, default


class Connector(QtCore.QObject):
    serverStateSignal = QtCore.pyqtSignal(dict)
    errorsSignal = QtCore.pyqtSignal(str)
    warningsSignal = QtCore.pyqtSignal(str)
    waxsStateSignal = QtCore.pyqtSignal(dict)
    saxsStateSignal = QtCore.pyqtSignal(dict)
    waxsPlotSignal = QtCore.pyqtSignal(dict)
    saxsPlotSignal = QtCore.pyqtSignal(dict)

    def __init__(self):
        super().__init__()
        self.buffer = b''
        self.header = b''
        self.size = 0
        self.unpackWaxsChi = False
        self.unpackSaxsChi = False
        self.saxsTimestamp = 0
        self.waxsTimestamp = 0
        self.localServer = False
        self.beamline = 'Dubble'
        self.host = default.DEFAULT_HOST
        self.port = default.DEFAULT_PORT
        self.socketTimer = QtCore.QTimer(self)
        self.socket = QtNetwork.QTcpSocket(self)
        self.serverHasStopped()
        self.connectTimer = QtCore.QTimer(self)
        self.connectSignals()
        self.connectTimer.start(1000)

    # noinspection PyUnresolvedReferences
    def connectSignals(self):
        self.socketTimer.timeout.connect(self.sendStateRequest)
        self.socket.connected.connect(self.sendFirstRequest)
        self.socket.readyRead.connect(self.readResponse)
        self.socket.disconnected.connect(self.serverHasStopped)
        self.socket.error.connect(self.serverHasError)
        self.connectTimer.timeout.connect(self.tryToConnect)

    def tryToConnect(self):
        if self.socket.state() == QtNetwork.QTcpSocket.UnconnectedState:
            self.connectToServer(self.host, self.port)

    def tryServer(self, host, port):
        if host in ('127.0.0.1', 'localhost', 'localhost6', 'localhost.localdomain'):
            self.localServer = True
        self.connectTimer.start(1000)
        self.connectToServer(host, port)

    def connectToServer(self, host, port):
        self.host = host
        self.port = port
        self.socket.close()
        self.socket.connectToHost(host, port)

    def sendFirstRequest(self):
        self.send({'state': 1, 'runLocally': self.localServer})
        self.socketTimer.start(1000)

    def sendStateRequest(self):
        self.send(self.stateRequest())

    def readResponse(self):
        self.buffer += bytes(self.socket.readAll())
        while len(self.buffer) >= default.PICKLE_HEADER_SIZE:
            if not self.header:
                self.header = self.buffer[:default.PICKLE_HEADER_SIZE]
                self.buffer = self.buffer[default.PICKLE_HEADER_SIZE:]
                magic, self.size = struct.unpack(default.PICKLE_HEADER_STRUCT, self.header)
                if magic != default.PICKLE_MAGIC_NUMBER:
                    self.header = b''
                    continue
            if len(self.buffer) < self.size:
                break
            packet = self.buffer[:self.size]
            self.buffer = self.buffer[self.size:]
            self.header = b''
            response = pickle.loads(packet)
            self.parseResponse(response)

    def serverHasStopped(self):
        self.serverStateSignal.emit({'serverRunning': ''})
        self.saxsStateSignal.emit({'saxs': {'running': False}})
        self.waxsStateSignal.emit({'waxs': {'running': False}})
        self.socketTimer.stop()
        self.socket.close()

    def serverHasError(self):
        pass

    def send(self, obj):
        obj['pickle'] = True
        request = '{}\r\n'.format(json.dumps(obj))
        if self.socket.state() == self.socket.ConnectedState:
            self.socket.write(request.encode(errors='ignore'))

    def stateRequest(self):
        return {'state': 1}

    def killRequest(self):
        return {'kill': 1}

    def parseResponse(self, response):
        if not response:
            return
        self.parseServerInfo(response.get('server', {}))
        self.parseWaxsResponse(response.get('waxs', {}))
        self.parseSaxsResponse(response.get('saxs', {}))
        if not self.parseErrorsResponse(response.get('errors', {})):
            self.parseWarningsResponse(response.get('warnings', {}))

    def parseErrorsResponse(self, errors):
        if errors:
            self.errorsSignal.emit(self.joinServerMessages(errors))
            return True
        return False

    def parseWarningsResponse(self, warnings):
        if warnings:
            self.warningsSignal.emit(self.joinServerMessages(warnings))

    def joinServerMessages(self, messages):
        return '\n'.join('{:d}. {}'.format(i, s) for i, s in enumerate(messages, 1))

    def unpackResponseArrays(self, response):
        data1d = response.get('data1d', None)
        image = response.get('image', None)
        if data1d:
            response['data1d'] = [compressor.decompressNumpyArray(a, False) for a in data1d]
        if image:
            response['image'] = compressor.decompressNumpyArray(image, False)
        return response

    def parseWaxsResponse(self, response):
        timestamp = response.get('timestamp', 0)
        if timestamp > self.waxsTimestamp:
            self.waxsTimestamp = timestamp
            response = self.unpackResponseArrays(response)
            self.waxsPlotSignal.emit(response)
        self.waxsStateSignal.emit(response)

    def parseSaxsResponse(self, response):
        timestamp = response.get('timestamp', 0)
        if timestamp > self.saxsTimestamp:
            self.saxsTimestamp = timestamp
            response = self.unpackResponseArrays(response)
            self.saxsPlotSignal.emit(response)
        self.saxsStateSignal.emit(response)

    def parseServerInfo(self, serverinfo):
        serverRuntime = self.parseServerTimestamp(serverinfo.get('startedTimestamp', 0))
        serverKilled = serverinfo.get('killed', True)
        self.serverStateSignal.emit({'serverRunning': serverRuntime, 'killed': serverKilled})

    def parseServerTimestamp(self, timestamp):
        serverStartedTimestamp = int((time.time() - timestamp) / 60)
        s = 'Server is running for'
        if serverStartedTimestamp < 60:
            minutes = serverStartedTimestamp
            runTime = '{} {} minute{}'.format(s, minutes, 's' if minutes > 1 else '')
        elif 60 <= serverStartedTimestamp < 60 * 24:
            hours = serverStartedTimestamp // 60
            minutes = serverStartedTimestamp - hours * 60
            runTime = '{} {:d} hour{} and {:d} minute{}'.format(s, hours, 's' if hours > 1 else '', minutes,
                                                                's' if minutes > 1 else '')
        else:
            days = serverStartedTimestamp // (60 * 24)
            hours = serverStartedTimestamp // 60 - days * 24
            minutes = serverStartedTimestamp - hours * 60 - days * 24 * 60
            runTime = '{} {:d} day{}, {:d} hour{} and {:d} minute{}'.format(s, days, 's' if days > 1 else '', hours,
                                                                            's' if hours > 1 else '', minutes,
                                                                            's' if minutes > 1 else '')
        return runTime

    def disconnectFromServer(self):
        self.socket.close()
        self.socketTimer.stop()
        self.connectTimer.stop()

    def killServer(self):
        self.send(self.killRequest())

    def getMask(self, maskFile, itype):
        mask = maskFile
        if os.path.exists(maskFile):
            try:
                mask = cryio.openImage(maskFile)
            except (IOError, cryio.numpymask.NotNumpyMask, cryio.fit2dmask.NotFit2dMask):
                pass
            else:
                mask = decor.correctMask(self.beamline, itype, mask).array
                mask[mask == 1] = -1
        return mask

    def packMask(self, params, itype):
        mask = self.getMask(params.get('maskFile', ''), itype)
        if isinstance(mask, np.ndarray):
            params['maskFile'] = compressor.compressNumpyArray(mask)

    def packPoni(self, params):
        poni = params.get('poni', '')
        if os.path.exists(poni):
            params['poni'] = compressor.compressFile(poni)

    def packBackground(self, params):
        pass

    def runSaxsWaxs(self, params, itype):
        self.packPoni(params)
        self.packBackground(params)
        self.packMask(params, itype)
        self.send({itype: params})

    def setBeamline(self, beamline):
        self.beamline = beamline
