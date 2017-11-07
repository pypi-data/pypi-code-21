#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: VeriCold.genesisPolarisFile
   :synopsis: Read genesis polaris file.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read genesis polaris file.
"""

###############################################################################
# Copyright 2007 Hendrix Demers
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

# Third party modules.
import numpy
import scipy.stats as stats

# Local modules.

# Project modules.

# Globals and constants variables.

# TODO: Test with a Polaris spectrum line scan file .pls
# TODO: Test with a Polaris spectrum mapping file .psd
# TODO: Test if the file size formula match the real file size.

class GenesisPolarisFile(object):
    def __init__(self, filepath=None):

        self.headerSize = 3072

        self.headerFormat = self.getHeaderFormat()

        #print "headerFormat size: %i (%i)" % (struct.calcsize(self.headerFormat), self.headerSize)
        assert self.headerSize == struct.calcsize(self.headerFormat)

        self.pixelTimesSize = 4

        self.pixelTimesFormat = "<L"

        #print "pixelTimesSize size: %i (%i)" % (struct.calcsize(self.pixelTimesFormat), self.pixelTimesSize)
        assert self.pixelTimesSize == struct.calcsize(self.pixelTimesFormat)

        self.cspDataSize = 8

        self.cspDataFormat = "<fL"

        #print "traceDataFormat size: %i (%i)" % (struct.calcsize("<"+self.traceDataFormat), self.traceDataSize)
        assert self.cspDataSize == struct.calcsize(self.cspDataFormat)

        self.reset()

        if filepath is not None:
            self.readFile(filepath)

    def reset(self):
        self.isFileRead = False

        self.header = {}

        self.pixelTimes = {}

    def getFileSize(self, filepath):
        return os.stat(filepath).st_size

    def getHeaderFormat(self):
        header_format = "<"

        # tag[16]
        header_format += "16s"
        # version
        header_format += "3l"

        # pixOffset
        header_format += "4L"

        # dwell
        header_format += "f"

        # TODO: find the correct header_format for date.
        # date
        header_format += "8s"

        # analyzerType
        header_format += "2l"

        # preset
        header_format += "12f"

        # nPeaks
        header_format += "l"

        # TODO: Find the correct header_format for Peaks.
        # Peaks[48]
        header_format += "384s"

        # nRemark
        header_format += "l"

        # TODO: Find the correct header_format for Remarks.
        # Remarks[10]
        header_format += "400s"

        # x
        header_format += "4f"

        # nDetRes
        header_format += "l"

        # detRes[12]
        header_format += "12f"

        # nStartX
        header_format += "4l"

        # Filler[1708]
        header_format += "1708s"

        # matLabel[40]
        header_format += "40s"

        # Filler[2]
        #header_format += "2s"

        # Label[216]
        header_format += "216s"

        # imgFilename[120]
        header_format += "120s"

        # TODO: finish all data in header.

        return header_format

    # TODO: Add the option to read only a fraction of the data for huge file.
    def readFile(self, filepath):
        if os.path.isfile(filepath):
            self.fileSize = self.getFileSize(filepath)

            #print self.fileSize

            self.header = self.readHeader(filepath)

            nPoints = self.header["nPoints"]

            nLines = self.header["nLines"]

            offset = self.header["pixOffset"]

            self.pixelTimes = self.readPixelTimes(filepath, nPoints, nLines, offset)

            cspDataSize = self.header["dataSize"]

            offset = self.header["dataOffset"]

            self.cspData = self.readCspData(filepath, cspDataSize, offset)

            self.isFileRead =    True

            return

    def readCspData(self, filepath, cspDataSize, offset):
        cspData = []

        cspFile = open(filepath, "rb")

        cspFile.seek(offset)

        for dummy_index in range(cspDataSize):
            cspDataStr = cspFile.read(self.cspDataSize)

            values = struct.unpack(self.cspDataFormat, cspDataStr)

            energy_eV = float(values[0])

            time = values[1]

            cspData.append((energy_eV, time))

        return cspData

    def readPixelTimes(self, filepath, nPoints, nLines, offset):
        pixelTimes = []

        numberPixels = nPoints*nLines

        cspFile = open(filepath, "rb")

        cspFile.seek(offset)

        for dummy_index in range(numberPixels):
            pixelTimesStr = cspFile.read(self.pixelTimesSize)

            values = struct.unpack(self.pixelTimesFormat, pixelTimesStr)

            pixelTime = values[0]

            pixelTimes.append(pixelTime)

        return pixelTimes

    def readHeader(self, filepath):
        cspFile = open(filepath, "rb")

        headerStr = cspFile.read(self.headerSize)

        values = struct.unpack(self.headerFormat, headerStr)

        #print len(values)

#        for index,value in enumerate(values):
#            print "%2i: >>%s<<" % (index, value)

        header = {}

        header["tag"] = values[0]

        header["version"] = values[1]
        header["nPoints"] = values[2]
        header["nLines"] = values[3]

        header["pixOffset"] = values[4]
        header["pixSize"] = values[5]
        header["dataOffset"] = values[6]
        header["dataSize"] = values[7]

        header["dwell"] = float(values[8])

        header["date"] = values[9]

        header["analyzerType"] = values[10]
        header["analysisMode"] = values[11]

        header["preset"] = float(values[12])
        header["liveTime"] = float(values[13])
        header["tilt"] = float(values[14])
        header["takeoff"] = float(values[15])
        header["XRayInc"] = float(values[16])
        header["azimuth"] = float(values[17])
        header["elevation"] = float(values[18])
        header["beamCurrent"] = float(values[19])
        header["kV"] = float(values[20])
        header["startEv"] = float(values[21])
        header["endEv"] = float(values[22])
        header["fullscale"] = float(values[23])

        return header

    def printHeader(self):
        keys = self.header.keys()
        keys.sort()

        for key in keys:
            print("%30s: %s" % (key, str(self.header[key])))

    # TODO: Get spectrum from a pixel.
    def getSpectrum(self, eVChannel=1.0, limits=None):

        if limits is not None:
            startEnergy_eV = limits[0]

            endEnergy_eV = limits[1]
        else:
            startEnergy_eV = self.header["startEv"]

            endEnergy_eV = self.header["endEv"]

        energies_eV = numpy.arange(startEnergy_eV, endEnergy_eV+eVChannel, eVChannel)

        data = [energy_eV for energy_eV, dummy_time in self.cspData]

        intensities = stats.histogram2(data, energies_eV)

        assert len(energies_eV) == len(intensities)

        #print len(self.cspData), sum(intensities)

        return energies_eV[:-1], intensities[:-1]

def run():
    import pylab

    filepath = os.path.expanduser("~/works/prgrms/pythondev/pySpectrumFileFormat/testData/k3670_30keV_OFeCalibration.csp")

    gpFile = GenesisPolarisFile(filepath)

    gpFile.printHeader()

    energies_eV, intensities = gpFile.getSpectrum()

    pylab.figure()

    pylab.plot(energies_eV, intensities)

    energies_eV, intensities = gpFile.getSpectrum(10.0)

    pylab.figure()

    pylab.plot(energies_eV, intensities)

    energies_eV, intensities = gpFile.getSpectrum(0.1)

    pylab.figure()

    pylab.plot(energies_eV, intensities)

    pylab.show()

if __name__ == '__main__':  # pragma: no cover
    run()
