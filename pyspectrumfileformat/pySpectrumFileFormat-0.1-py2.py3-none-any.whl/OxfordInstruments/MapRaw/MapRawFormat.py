#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: OxfordInstruments.MapRaw.MapRawFormat
   :synopsis: Read Oxford Instruments map in the raw format.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read Oxford Instruments map in the raw format.
"""

###############################################################################
# Copyright 2012 Hendrix Demers
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###############################################################################

# Standard library modules.
import os.path
import struct
import logging

# Third party modules.
import matplotlib.pyplot as plt
import numpy as np

# Local modules.

# Project modules.
import pySpectrumFileFormat.OxfordInstruments.MapRaw.ParametersFile as ParametersFile

# Globals and constants variables.

class MapRawFormat(object):
    def __init__(self, rawFilepath):
        logging.info("Raw file: %s", rawFilepath)

        self._rawFilepath = rawFilepath
        parametersFilepath = self._rawFilepath.replace('.raw', '.rpl')

        self._parameters = ParametersFile.ParametersFile()
        self._parameters.read(parametersFilepath)

        self._format = self._generateFormat(self._parameters)

    def _generateFormat(self, parameters):
        spectrumFormat = ""
        if parameters.byteOrder == ParametersFile.BYTE_ORDER_LITTLE_ENDIAN:
            spectrumFormat += '<'

        if parameters.dataLength_B == 1:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "b"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "B"
        elif parameters.dataLength_B == 2:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "h"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "H"
        elif parameters.dataLength_B == 4:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "i"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "I"

        logging.info("Format: %s", spectrumFormat)

        return spectrumFormat

    def _generateSumSpectraFormat(self, parameters):
        spectrumFormat = ""
        if parameters.byteOrder == ParametersFile.BYTE_ORDER_LITTLE_ENDIAN:
            spectrumFormat += '<'

        spectrumFormat += '%i' % (parameters.width*parameters.height)

        if parameters.dataLength_B == 1:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "b"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "B"
        elif parameters.dataLength_B == 2:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "h"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "H"
        elif parameters.dataLength_B == 4:
            if parameters.dataType == ParametersFile.DATA_TYPE_SIGNED:
                spectrumFormat += "i"
            elif parameters.dataType == ParametersFile.DATA_TYPE_UNSIGNED:
                spectrumFormat += "I"

        logging.info("Format: %s", spectrumFormat)

        return spectrumFormat

    def getSpectrum(self, pixelId):
        logging.debug("Pixel ID: %i", pixelId)

        imageOffset = self._parameters.width*self._parameters.height
        logging.debug("File offset: %i", imageOffset)

        logging.debug("Size: %i", struct.calcsize(self._format))

        x = np.arange(0, self._parameters.depth)
        y = np.zeros_like(x)
        rawFile = open(self._rawFilepath, 'rb')
        for channel in range(self._parameters.depth):
            fileOffset = self._parameters.offset + (pixelId + channel*imageOffset)*self._parameters.dataLength_B
            rawFile.seek(fileOffset)
            fileBuffer = rawFile.read(struct.calcsize(self._format))
            items = struct.unpack(self._format, fileBuffer)
            y[channel] = float(items[0])

        rawFile.close()

        return x, y

    def getSumSpectrum(self):
        imageOffset = self._parameters.width*self._parameters.height
        x = np.arange(0, self._parameters.depth)
        y = np.zeros_like(x)
        rawFile = open(self._rawFilepath, 'rb')
        fileOffset = self._parameters.offset
        rawFile.seek(fileOffset)

        sumSpectrumformat = self._generateSumSpectraFormat(self._parameters)

        for channel in range(self._parameters.depth):
            logging.info("Channel: %i", channel)
            fileBuffer = rawFile.read(struct.calcsize(sumSpectrumformat))
            items = struct.unpack(sumSpectrumformat, fileBuffer)
            y[channel] = np.sum(items)

        rawFile.close()

        return x, y

    def getSumSpectrumOld(self):
        numberPixels = self._parameters.width*self._parameters.height
        logging.info("Numbe rof pixels: %i", numberPixels)

        x = np.arange(0, self._parameters.depth)
        ySum = np.zeros_like(x)

        for pixelId in range(numberPixels):
            _x, y = self.getSpectrum(pixelId)
            ySum += y

        return x, ySum

def run():
    path = r"J:\hdemers\work\mcgill2012\results\experimental\McGill\su8000\others\exampleEDS"
    #filename = "Map30kV.raw"
    filename = "Project 1.raw"
    filepath = os.path.join(path, filename)

    mapRaw = MapRawFormat(filepath)

    line = 150
    column = 150
    pixelId = line + column*512
    xData, yData = mapRaw.getSpectrum(pixelId=pixelId)

    plt.figure()
    plt.plot(xData, yData)

    xData, yData = mapRaw.getSumSpectrum()

    plt.figure()
    plt.plot(xData, yData)
    plt.show()

def run20120307():
    path = r"J:\hdemers\work\mcgill2012\results\experimental\McGill\su8000\hdemers\20120307\rareearthSample"
    filename = "mapSOI_15.raw"
    filepath = os.path.join(path, filename)

    mapRaw = MapRawFormat(filepath)

    line = 150
    column = 150
    pixelId = line + column*512
    xData, yData = mapRaw.getSpectrum(pixelId=pixelId)

    plt.figure()
    plt.plot(xData, yData)
    plt.show()

if __name__ == '__main__':  # pragma: no cover
    run()
