#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time


class PylatusChunkObject:
    def __init__(self):
        self.timestamp = time.time()


class PylatusExperimentFinished(PylatusChunkObject):
    pass


class PylatusExperimentParams(PylatusChunkObject):
    beamX = 0
    beamY = 0
    cbf = ''
    cbfBaseName = ''
    cbfName = ''
    expPeriod = 0
    kappa = 0
    mod = 0
    mod2 = 0
    nframes = 0
    nop = False
    omegaphi = 0
    oscAxis = ''
    path = ''
    period = 0
    periods = 0
    pixelX = 0
    pldistd = 0
    pldistf = 0
    plrot = 0
    plvert = 0
    startAngle = 0
    step = 0
    userSubDir = ''
    zeroDistance = 0
    omega = 0
    omegastep = 0
    phi = 0
    phistep = 0


class PylatusExperimentValue(PylatusChunkObject):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def key(self):
        return self.__class__.__name__[7:]

    def __repr__(self):
        return f'{self.timestamp}: {self.value}'


class PylatusFlux(PylatusExperimentValue):
    pass


class PylatusTemperature(PylatusExperimentValue):
    pass


class PylatusBlower(PylatusExperimentValue):
    pass


class PylatusLakeshore(PylatusExperimentValue):
    pass


class PylatusScanParams(PylatusExperimentParams):
    auto = True
    axis = ''
    start = 0
    stop = 0
    nfilter = 0
    backup = 0
    images = set()
