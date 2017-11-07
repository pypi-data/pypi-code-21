#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.emmff.emsaFormat
   :synopsis: Reader/writer of EMSA/MAS file format.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Reader/writer of EMSA/MAS file format.
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
import logging

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.

class RequiredKeyword:
    format = "FORMAT"
    version = "VERSION"
    title = "TITLE"
    date = "DATE"
    time = "TIME"
    owner = "OWNER"
    numberPoints = "NPOINTS"
    numberColumns = "NCOLUMNS"
    xUnits = "XUNITS"
    yUnits = "YUNITS"
    dataType = "DATATYPE"
    xPerChannel = "XPERCHAN"
    offset = "OFFSET"

class SpectrumDataKeyword:
    spectrum = "SPECTRUM"
    endOfData = "ENDOFDATA"

class OptionalKeyword:
    # Keywords relating mainly to spectrum characteristics.
    signalType = "SIGNALTYPE"
    xUnits = "XUNITS"
    yUnits = "YUNITS"
    xLabel = "XLABEL"
    yLabel = "YLABEL"
    channelOffset = "CHOFFSET"
    comment = "COMMENT"
    # Keywords relating mainly to microscope/instrument.
    beamEnergy = "BEAMKV"
    emissionCurrent = "EMISSION"
    probeCurrent = "PROBECUR"
    beamDiameter = "BEAMDIAM"
    magnification = "MAGCAM"
    convergenceAngle = "CONVANGLE"
    operatingMode = "OPERMODE"
    # Keywords relating mainly to specimen.
    thickness = "THICKNESS"
    xStageTilt = "XTILISTGE"
    yStageTilt = "YTILISTGE"
    xPosition = "XPOSITION"
    yPosition = "YPOSITION"
    zPosition = "ZPOSITION"
    # Keywords relating mainly to ELS.
    dwellTime = "DWELLTIME"
    integrationTime = "INTEGTIME"
    collectionAngle = "COLLANGLE"
    elsDetectorType = "ELSDET"
    # Keywords relating mainly to EDS.
    elevationAngle = "ELEVANGLE"
    azimuthalAngle = "AZIMANGLE"
    solidAngle = "SOLIDANGLE"
    liveTime = "LIVETIME"
    realTime = "REALTIME"
    beWindowThickness = "TBEWIND"
    auContactThickness = "TAUWIND"
    deadLayerThickness = "TDEADLYR"
    activeLayerThickness = "TACTLYR"
    aluminiumWindowThickness = "TALWIND"
    pyroleneWindowThickness = "TPYWIND"
    boronNitrideWindowThickness = "TBNWIND"
    diamondWindowThickness = "TDIWIND"
    hydroCarbonWindowThickness = "THCWIND"
    edsDetectorType = "EDSDET"
    checksum = "CHECKSUM"

class OptionalUserDefinedKeyword:
    class OxfordInstruments:
        element = "OXINSTELEMS"
        label = "OXINSTLABEL"

class EmsaFormat:

    def __init__(self, filename=None, lines=None):
        self.lines = lines
        self.filename = filename
        self.values = []
        self.xData = []
        self.yData = []

        self.keywords = []

        self.header = {}

        self.isFileValid = None

        self.setFunction = {}
        self.setFunction[RequiredKeyword.format] = 'setFormat'
        self.setFunction[RequiredKeyword.version] = 'setVersion'
        self.setFunction[RequiredKeyword.title] = 'setTitle'
        self.setFunction[RequiredKeyword.date] = 'setDate'
        self.setFunction[RequiredKeyword.time] = 'setTime'
        self.setFunction[RequiredKeyword.owner] = 'setOwner'
        self.setFunction[RequiredKeyword.numberPoints] = 'setNumberPoints'
        self.setFunction[RequiredKeyword.numberColumns] = 'setNumberColumns'
        self.setFunction[RequiredKeyword.xUnits] = 'setXUnits'
        self.setFunction[RequiredKeyword.yUnits] = 'setYUnits'
        self.setFunction[RequiredKeyword.dataType] = 'setDataType'
        self.setFunction[RequiredKeyword.xPerChannel] = 'setXPerChannel'
        self.setFunction[RequiredKeyword.offset] = 'setOffset'

        self.setFunction[OptionalKeyword.signalType] = 'setSignalType'
        self.setFunction[OptionalKeyword.channelOffset] = 'setChannelOffset'
        self.setFunction[OptionalKeyword.liveTime] = 'setLiveTime'
        self.setFunction[OptionalKeyword.realTime] = 'setRealTime'
        self.setFunction[OptionalKeyword.beamEnergy] = 'setBeamEnergy'
        self.setFunction[OptionalKeyword.probeCurrent] = 'setProbeCurrent'
        self.setFunction[OptionalKeyword.magnification] = 'setMagnification'
        self.setFunction[OptionalKeyword.xPosition] = 'setXPosition'
        self.setFunction[OptionalKeyword.yPosition] = 'setYPosition'
        self.setFunction[OptionalKeyword.zPosition] = 'setZPosition'

        self.setFunction[OptionalUserDefinedKeyword.OxfordInstruments.element] = 'setOxfordInstrumentsElement'
        self.setFunction[OptionalUserDefinedKeyword.OxfordInstruments.label] = 'setOxfordInstrumentsLabel'

        if self.filename != None:
            self.open(self.filename)
            self.readLines()
            self.setHeader()
            self.setSpectrumData()

    def open(self, filename):
        try:
            self.lines = open(filename).readlines()
        except:
            raise IOError

    def isLineData(self, line):
        """Check if the line is a valide data. Return True or False, type (Y, XY),
        and number of column (1--5)."""

        if line is None or line.strip().startswith('#'):
            return False, None, 0

        dataType = self.getDataType()

        if dataType == 'Y':
            # Y with 1 column
            try:
                yValue = float(line)

                return True, 'Y', 1
            except:
                pass

            # Y with comma 2 to 5 column
            try:
                yValueList = []
                yValueList = line.split(',')

                if len(yValueList) > 1 and len(yValueList) <= 5:
                    newYValues = []
                    for yValue in yValueList:
                        try:
                            yValue = float(yValue)
                            newYValues.append(yValue)
                        except ValueError:
                            pass

                    return True, 'Y', len(newYValues)
            except:
                pass

            # Y with space 2 to 5 column
            try:
                yValueList = []
                yValueList = line.split()

                if len(yValueList) > 1 and len(yValueList) <= 5:
                    for yValue in yValueList:
                        yValue = float(yValue)

                    return True, 'Y', len(yValueList)
            except:
                pass
        elif dataType == 'XY':
            # XY with comma
            try:
                (xValue, yValue) = line.split(',')

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass

            # XY with comma
            try:
                xValue, yValue, dummy = line.split(',')

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass

            # XY with space
            try:
                (xValue, yValue) = line.split()

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass
        else:
            # Y with 1 column
            try:
                yValue = float(line)

                return True, 'Y', 1
            except:
                pass

            # Y with comma 2 to 5 column
            try:
                yValueList = []
                yValueList = line.split(',')

                if len(yValueList) > 1 and len(yValueList) <= 5:
                    numberValues = 0
                    for yValue in yValueList:
                        try:
                            yValue = float(yValue)
                            numberValues += 1
                        except ValueError:
                            pass

                    return True, 'Y', numberValues
            except:
                pass

            # Y with space 2 to 5 column
            try:
                yValueList = []
                yValueList = line.split()

                if len(yValueList) > 1 and len(yValueList) <= 5:
                    for yValue in yValueList:
                        yValue = float(yValue)

                    return True, 'Y', len(yValueList)
            except:
                pass

            # XY with comma
            try:
                (xValue, yValue) = line.split(',')

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass

            # XY with comma
            try:
                xValue, yValue, dummy = line.split(',')

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass

            # XY with space
            try:
                (xValue, yValue) = line.split()

                xValue = float(xValue)
                yValue = float(yValue)

                return True, 'XY', 2
            except:
                pass

        return False, None, 0

    def isLineKeyword(self, line):
        try:
            if line.strip()[0] == '#':
                return True
        except:
            pass

        return False

    def readKeywordLine(self, line):
        startKeywordPosition = 1
        endKeywordPosition = 13
        startDataPosition = 15

        try:
            if line[0] == '#':
                if line[1] == '#':
                    keyword = line[startKeywordPosition+1:endKeywordPosition]
                    data = line[startDataPosition:]
                else:
                    keyword = line[startKeywordPosition:endKeywordPosition]
                    data = line[startDataPosition:]

                keyword = keyword.strip()
                keywordComment = ""

                try:
                    newKeyword, keywordComment = keyword.split()
                    keyword = newKeyword
                except:
                    pass

                keyword = keyword.strip()
                keyword = keyword.upper()

                keywordComment = keywordComment.strip()

                data = data.strip()

            return (keyword, keywordComment, data)
        except:
            pass

        return (None, None, None)

    def readDataLine(self, line):
        try:
            values = []
            values = line.split()
            for index, item in enumerate(values):
                values[index] = float(item)
            return values
        except:
            values = None

        try:
            values = []
            for index, item in enumerate(line.split(',')):
                try:
                    values.append(float(item))
                except ValueError:
                    pass
            if len(values) > 0:
                return values
            else:
                return None
        except:
            pass

        return None

    def readLine(self, line):
        if self.isLineKeyword(line):
            keyword, keywordComment, data = self.readKeywordLine(line)
            if keyword:
                keywordData = {}
                keywordData["keyword"] = keyword
                keywordData["comment"] = keywordComment
                keywordData["data"] = data
                keywordData["order"] = len(self.keywords)+1

                self.keywords.append(keywordData)

        if self.isLineData(line)[0]:
            values = self.readDataLine(line)
            if values:
                self.values.append(values)

    def readLines(self):
        if self.lines:
            for line in self.lines:
                self.readLine(line)

    def setHeader(self):
        checkOrder = 0
        self.isFileValid = True

        for keyword in self.keywords:
            checkOrder += 1
            for variable in RequiredKeyword.__dict__.keys():
                if RequiredKeyword.__dict__.get(variable, None) == keyword["keyword"]:
                    if RequiredKeyword.__dict__[variable] in self.setFunction:
                        EmsaFormat.__dict__[self.setFunction[RequiredKeyword.__dict__[variable]]](self, keyword["data"])
                        if checkOrder != keyword["order"]:
                            print("Warning keyword in the wrong order.")
                            self.isFileValid = False

            for variable in OptionalKeyword.__dict__.keys():
                if OptionalKeyword.__dict__.get(variable, None) == keyword["keyword"]:
                    if OptionalKeyword.__dict__[variable] in self.setFunction:
                        EmsaFormat.__dict__[self.setFunction[OptionalKeyword.__dict__[variable]]](self, keyword["data"])
                        if checkOrder != keyword["order"]:
                            print("Warning keyword in the wrong order.")
                            self.isFileValid = False

            for variable in OptionalUserDefinedKeyword.OxfordInstruments.__dict__.keys():
                if OptionalUserDefinedKeyword.OxfordInstruments.__dict__.get(variable, None) == keyword["keyword"]:
                    if OptionalUserDefinedKeyword.OxfordInstruments.__dict__[variable] in self.setFunction:
                        EmsaFormat.__dict__[self.setFunction[OptionalUserDefinedKeyword.OxfordInstruments.__dict__[variable]]](self, keyword["data"])
                        if checkOrder != keyword["order"]:
                            print("Warning keyword in the wrong order.")
                            self.isFileValid = False

    def setFormat(self, newFormat):
        self.header[RequiredKeyword.format] = newFormat

    def getFormat(self):
        return self.header.get(RequiredKeyword.format, None)

    def setVersion(self, newVersion):
        self.header[RequiredKeyword.version] = newVersion

    def getVersion(self):
        return self.header.get(RequiredKeyword.version, None)

    def setTitle(self, newValue):
        self.header[RequiredKeyword.title] = newValue

    def getTitle(self):
        return self.header.get(RequiredKeyword.title, None)

    def setDate(self, newValue):
        self.header[RequiredKeyword.date] = newValue

    def getDate(self):
        return self.header.get(RequiredKeyword.date, None)

    def setTime(self, newValue):
        self.header[RequiredKeyword.time] = newValue

    def getTime(self):
        return self.header.get(RequiredKeyword.time, None)

    def setOwner(self, newValue):
        self.header[RequiredKeyword.owner] = newValue

    def getOwner(self):
        return self.header.get(RequiredKeyword.owner, None)

    def setNumberPoints(self, newValue):
        self.header[RequiredKeyword.numberPoints] = float(newValue)

    def getNumberPoints(self):
        return self.header.get(RequiredKeyword.numberPoints, None)

    def setNumberColumns(self, newValue):
        self.header[RequiredKeyword.numberColumns] = float(newValue)

    def getNumberColumns(self):
        return self.header.get(RequiredKeyword.numberColumns, None)

    def setXUnits(self, newValue):
        self.header[RequiredKeyword.xUnits] = newValue

    def getXUnits(self):
        return self.header.get(RequiredKeyword.xUnits, None)

    def setYUnits(self, newValue):
        self.header[RequiredKeyword.yUnits] = newValue

    def getYUnits(self):
        return self.header.get(RequiredKeyword.yUnits, None)

    def setDataType(self, newValue):
        self.header[RequiredKeyword.dataType] = newValue

    def getDataType(self):
        return self.header.get(RequiredKeyword.dataType, None)

    def setXPerChannel(self, newValue):
        self.header[RequiredKeyword.xPerChannel] = float(newValue)

    def getXPerChannel(self):
        return self.header.get(RequiredKeyword.xPerChannel, None)

    def setOffset(self, newValue):
        self.header[RequiredKeyword.offset] = float(newValue)

    def getOffset(self):
        return self.header.get(RequiredKeyword.offset, None)

    def setSignalType(self, newValue):
        self.header[OptionalKeyword.signalType] = newValue

    def getSignalType(self):
        return self.header.get(OptionalKeyword.signalType, None)

    def setChannelOffset(self, newValue):
        self.header[OptionalKeyword.channelOffset] = float(newValue)

    def getChannelOffset(self):
        return self.header.get(OptionalKeyword.channelOffset, None)

    def setLiveTime(self, newValue):
        self.header[OptionalKeyword.liveTime] = float(newValue)

    def getLiveTime(self):
        return self.header.get(OptionalKeyword.liveTime, None)

    def setRealTime(self, newValue):
        self.header[OptionalKeyword.realTime] = float(newValue)

    def getRealTime(self):
        return self.header.get(OptionalKeyword.realTime, None)

    def setBeamEnergy(self, newValue):
        self.header[OptionalKeyword.beamEnergy] = float(newValue)

    def getBeamEnergy(self):
        return self.header.get(OptionalKeyword.beamEnergy, None)

    def setProbeCurrent(self, newValue):
        self.header[OptionalKeyword.probeCurrent] = float(newValue)

    def getProbeCurrent(self):
        return self.header.get(OptionalKeyword.probeCurrent, None)

    def setMagnification(self, newValue):
        self.header[OptionalKeyword.magnification] = float(newValue)

    def getMagnification(self):
        return self.header.get(OptionalKeyword.magnification, None)

    def setXPosition(self, newValue):
        self.header[OptionalKeyword.xPosition] = float(newValue)

    def getXPosition(self):
        return self.header.get(OptionalKeyword.xPosition, None)

    def setYPosition(self, newValue):
        self.header[OptionalKeyword.yPosition] = float(newValue)

    def getYPosition(self):
        return self.header.get(OptionalKeyword.yPosition, None)

    def setZPosition(self, newValue):
        self.header[OptionalKeyword.zPosition] = float(newValue)

    def getZPosition(self):
        return self.header.get(OptionalKeyword.zPosition, None)

    def setOxfordInstrumentsElement(self, newValue):
        self.header[OptionalUserDefinedKeyword.OxfordInstruments.element] = newValue

    def getOxfordInstrumentsElement(self):
        return self.header.get(OptionalUserDefinedKeyword.OxfordInstruments.element, None)

    def setOxfordInstrumentsLabel(self, newValue):
        self.header[OptionalUserDefinedKeyword.OxfordInstruments.label] = newValue

    def getOxfordInstrumentsLabel(self):
        return self.header.get(OptionalUserDefinedKeyword.OxfordInstruments.label, None)

    def setSpectrumData(self):
        dataType = self.getDataType()
        numberColumns = self.getNumberColumns()

        if dataType and numberColumns:
            for values in self.values:
                if dataType == "XY":
                    try:
                        self.xData.append(values[0])
                        self.yData.append(values[1])
                    except IndexError as message:
                        logging.error(message)
                        logging.info(values)
                        logging.info(self.filename)
                elif dataType == "Y":
                    for item in values:
                        if isinstance(item, list):
                            self.yData.extend(item)
                        else:
                            self.yData.append(item)
            if dataType == "Y":
                numberPoints = self.getNumberPoints()
                if len(self.yData) != numberPoints:
                    numberPoints = len(self.yData)

                self.xData = self.createXData(numberPoints, self.getOffset(), self.getXPerChannel())

    def getDataX(self):
        return self.xData

    def getDataY(self):
        return self.yData

    def getData(self):
        data = []
        assert(len(self.xData) == len(self.yData))
        for index in range(len(self.xData)):
            data.append((self.xData[index], self.yData[index]))

        return data

    def createXData(self, numberPoints, offset, xPerChannel):
        xData = []
        for index in range(int(numberPoints)):
            xData.append(offset + xPerChannel*index)

        return xData
