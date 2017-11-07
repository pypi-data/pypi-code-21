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
import logging

# Third party modules.
import matplotlib.pyplot as plt
import numpy as np

# Local modules.

# Project modules.
import pySpectrumFileFormat.Bruker.MapRaw.ParametersFile as ParametersFile

# Globals and constants variables.

class MapRawFormat(object):
    def __init__(self, rawFilepath):
        logging.info("Raw file: %s", rawFilepath)

        self._rawFilepath = rawFilepath
        parametersFilepath = self._rawFilepath.replace('.raw', '.rpl')

        self._parameters = ParametersFile.ParametersFile()
        self._parameters.read(parametersFilepath)

        self._data = None

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

    def _generateSpectraFormatVector(self, parameters):
        spectrumFormat = ""
        if parameters.byteOrder == ParametersFile.BYTE_ORDER_LITTLE_ENDIAN:
            spectrumFormat += '<'

        spectrumFormat += '%i' % (parameters.depth)

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

        logging.debug("Format: %s", spectrumFormat)

        return spectrumFormat

    def _generateSumSpectraFormatVector(self, parameters):
        spectrumFormat = ""
        if parameters.byteOrder == ParametersFile.BYTE_ORDER_LITTLE_ENDIAN:
            spectrumFormat += '<'

        numberPixels = parameters.width*parameters.height

        spectrumFormat += '%i' % (parameters.depth*numberPixels)

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

        logging.debug("Format: %s", spectrumFormat)

        return spectrumFormat

    def getSpectrum(self, pixelX, pixelY):
        imageOffset = self._parameters.width*self._parameters.height
        logging.debug("File offset: %i", imageOffset)

        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            spectrum = self._data[:, pixelY, pixelX]

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            spectrum = self._data[pixelY, pixelX, :]

        channels = np.arange(0, self._parameters.depth)

        assert len(channels) == len(spectrum)
        return channels, spectrum

    def getDataCube(self):

        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            datacube = self._data[:, :, :]
            print(datacube.shape)
            datacube = np.rollaxis(datacube, 0, 3)
            print(datacube.shape)

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            datacube = self._data[:, :, :]

        channels = np.arange(0, self._parameters.depth)

        return channels, datacube

    def getROISpectrum(self, pixelXmin, pixelXmax, pixelYmin, pixelYmax):
        imageOffset = self._parameters.width*self._parameters.height
        logging.debug("File offset: %i", imageOffset)

        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            spectrum = np.sum(self._data[:, pixelYmin:pixelYmax+1, pixelXmin:pixelXmax+1], axis=(1,2))

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            spectrum = np.sum(self._data[pixelYmin:pixelYmax+1, pixelXmin:pixelXmax+1, :], axis=(0,1))

        channels = np.arange(0, self._parameters.depth)

        assert len(channels) == len(spectrum)
        return channels, spectrum

    def getSumSpectrum(self):
        x = np.arange(0, self._parameters.depth)
        y = np.zeros_like(x)

        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            raise NotImplementedError

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            y = self._data.sum(axis=(0, 1))

        assert len(x) == len(y)
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

    def getTotalIntensityImage(self):
        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            image = np.sum(self._data, axis=0)

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            image = np.sum(self._data, axis=2)

        return image

    def getRoiIntensityImage(self, channelRange):
        channel_min, channel_max = channelRange

        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            image = np.sum(self._data[channel_min:channel_max, ...], axis=0)

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            image = np.sum(self._data[...,channel_min:channel_max], axis=2)

        return image

    def getMaximumPixelSpectrum(self):
        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            spectrum = np.amax(self._data, axis=(1,2))

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            spectrum = np.amax(self._data, axis=(0,1))

        channels = np.arange(0, self._parameters.depth)

        assert len(channels) == len(spectrum)
        return channels, spectrum

    def getMaximumPixelSpectrumPixels(self):
        self._read_data()
        flat_pixels = np.zeros(self._parameters.depth)

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            flat_pixels = np.argmax(self._data, axis=0)

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            for channel in np.arange(0, self._parameters.depth):
                flat_pixels[channel] = np.argmax(self._data[:,:,channel])


        pixels = []
        for pixel in flat_pixels:
            j = int(pixel/self._parameters.width)
            i = int(pixel % self._parameters.width)
            pixels.append((i, j))

        return pixels

    def getMaximumPixelSpectrum2(self):
        self._read_data()
        channels = np.arange(0, self._parameters.depth)
        spectrum = np.zeros_like(channels)

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            spectrum = np.amax(self._data, axis=(1,2))

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            for channel in channels:
                spectrum[channel] = np.amax(self._data[:,:,channel])

        assert len(channels) == len(spectrum)
        return channels, spectrum

    def getTotalSpectrum(self):
        self._read_data()

        if self._parameters.recordBy == ParametersFile.RECORED_BY_IMAGE:
            spectrum = np.sum(self._data, axis=(1,2))

        elif self._parameters.recordBy == ParametersFile.RECORED_BY_VECTOR:
            spectrum = np.sum(self._data, axis=(0,1))

        channels = np.arange(0, self._parameters.depth)

        assert len(channels) == len(spectrum)
        return channels, spectrum

    def getParameters(self):
        return self._parameters

    def _read_data(self):
        mmap_mode = 'c'
        if self._data is None:
            if self._parameters.dataType == 'signed':
                data_type = 'int'
            elif self._parameters.dataType == 'unsigned':
                data_type = 'uint'
            elif self._parameters.dataType == 'float':
                pass
            else:
                raise TypeError('Unknown "data-type" string.')

            if self._parameters.byteOrder == 'big-endian':
                endian = '>'
            elif self._parameters.byteOrder == 'little-endian':
                endian = '<'
            else:
                endian = '='

            data_type = data_type + str(int(self._parameters.dataLength_B) * 8)
            data_type = np.dtype(data_type)
            data_type = data_type.newbyteorder(endian)

            self._data = np.memmap(self._rawFilepath, offset=self._parameters.offset, dtype=data_type, mode=mmap_mode)

            if self._parameters.recordBy == 'vector':
                shape = (self._parameters.height, self._parameters.width, self._parameters.depth)
                self._data = self._data.reshape(shape)
            elif self._parameters.recordBy == 'image':
                shape = (self._parameters.depth, self._parameters.height, self._parameters.width)
                self._data = self._data.reshape(shape)
            elif self._parameters.recordBy == 'dont-care':
                shape = (self._parameters.height, self._parameters.width)
                self._data = self._data.reshape(shape)

def run():
    path = r"F:\backup_su8230\bruker_data\Quantax User\edx\Data\2015\Demopoulos\Christine\D3-900"
    #filename = "Map30kV.raw"
    filename = "D3-900-map4.raw"
    filepath = os.path.join(path, filename)

    mapRaw = MapRawFormat(filepath)

    channels, datacube = mapRaw.getDataCube()
    plt.figure()
    plt.plot(channels, datacube[100,100,:])

    line = 150
    column = 150
    pixelId = line + column*512
    xData, yData = mapRaw.getSpectrum(line, column)

    plt.figure()
    plt.plot(xData, yData)

    xData, yData = mapRaw.getSumSpectrum()

    plt.figure()
    plt.plot(xData, yData)

    path = r"G:\backup_su8000\eds_ebsd\2010-2013-EDS\HDemers\AuCuStandard"
    filename = r"20130701_AuMap.raw"
    filepath = os.path.join(path, filename)

    mapRaw = MapRawFormat(filepath)

    channels, datacube = mapRaw.getDataCube()
    plt.figure()
    plt.plot(channels, datacube[0,0,:])

    plt.show()

def run20120307():
    path = r"G:\backup_su8000\eds_ebsd\2010-2013-EDS\HDemers\20120307\rareearthSample"
    filename = "D3-900-map4.raw"
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
