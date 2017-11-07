#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.EPMA.JEOL8900McGill
   :synopsis: Read the McGill JEOL 8900 EPMA data.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read the McGill JEOL 8900 EPMA data.
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
import warnings

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.

class DataPoint(object):
    def __init__(self):
        pass

    def readIDline(self, line):
        start = len('Unknown Specimen No.')

        specimenID = int(line[start:])

        return specimenID

    def readGroupSampleLine(self, line):
        group = line[16:32].strip()

        sample = line[42:].strip()

        return group, sample

    def readNumberCommentLine(self, line):
        number = int(line[16:32].strip())

        comment = line[42:].strip()

        return number, comment

    def readStageLine(self, line):
        stageX = float(line[22:33].strip())

        stageY = float(line[36:47].strip())

        stageZ = float(line[50:].strip())

        return stageX, stageY, stageZ

    def readBeamLine(self, line):
        incidentEnergy_keV = float(line[16:24].strip())

        probeDiameter = float(line[45:50].strip())

        scanOn = line[57:].strip()

        if scanOn == 'Off':
            scanOn = False
        else:
            scanOn = True

        return incidentEnergy_keV, probeDiameter, scanOn

    def readDateline(self, line):
        start = len(' Dated on')

        date = line[start:].strip()

        return date

    def readDetectorLine(self, line):
        detectorType = line[:16].strip()

        numberAccumulation = int(line[38:].strip())

        return detectorType, numberAccumulation

    def readCurrentLine(self, line):
        current_A = float(line[11:].strip())

        return current_A

    def getPositions(self, lines):
        positions = {}

        for line in lines:
            if 'Element Peak(mm)' in line:
                index = lines.index(line)
                positions['intensity'] = (index+1, 0)

            if 'Element  f(chi)' in line:
                index = lines.index(line)
                positions['correction'] = (index+1, 0)
                positions['intensity'] = (positions['intensity'][0], index)

            if 'Element  El. Wt%' in line:
                index = lines.index(line)
                positions['concentration'] = (index+1, 0)
                positions['correction'] = (positions['correction'][0], index)

            if 'Total:' in line:
                index = lines.index(line)
                positions['total'] = (index, index+1)
                positions['concentration'] = (positions['concentration'][0], index-1)

        return positions

    def increaseValueIndex(self, valueIndex, values, symbol, label, elementData):
        valueIndex += 1

        if valueIndex < len(values) and values[valueIndex] == '?':
            message = "Suspect value for element %s, %s = %0.4f" % (symbol, label, elementData[symbol][label])
            warnings.warn(message)

            valueIndex += 1

        return valueIndex

    def readIntensityLines(self, lines, elementData):
        for line in lines:
            line = line.strip()

            if len(line) > 0:
                values = line.split()

                symbol = values[1]

                elementData.setdefault(symbol, {})

                elementData[symbol]['id'] = int(values[0])

                valueIndex = 2

                label = 'peak_mm'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'net_cps'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'bg-_cps'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'bg+_cps'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'sd_%%'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'dl_ppm'
                elementData[symbol][label] = float(values[valueIndex])

                self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

    def readCorrectionLines(self, lines, elementData):
        for line in lines:
            line = line.strip()

            if len(line) > 0:
                values = line.split()

                symbol = values[0]

                elementData.setdefault(symbol, {})

                valueIndex = 1

                label = 'f(chi)'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'If/Ip'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'abs-el'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = '1/s-el'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'r-el'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'c/k-el'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'c/k-std'
                elementData[symbol][label] = float(values[valueIndex])

                self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

    def readConcentrationLines(self, lines, elementData):
        for line in lines:
            line = line.strip()

            if len(line) > 0:
                values = line.split()

                symbol = values[0]

                elementData.setdefault(symbol, {})

                valueIndex = 1

                label = 'El fw'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'Ox fw'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'Norm El'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'Norm Ox'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'Atomic'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'k-value'
                elementData[symbol][label] = float(values[valueIndex])

                valueIndex = self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

                label = 'k-std'
                elementData[symbol][label] = float(values[valueIndex])

                self.increaseValueIndex(valueIndex, values, symbol, label, elementData)

    def readTotalLines(self, lines, elementData):
        values = lines[0][7:].split()

        elementData['total'] = {}

        elementData['total']['El fw'] = float(values[0])

        elementData['total']['Ox fw'] = float(values[1])

        elementData['total']['Norm El'] = float(values[2])

        elementData['total']['Norm Ox'] = float(values[3])

        elementData['total']['Atomic'] = float(values[4])

    def readLines(self, lines):
        # pylint: disable-msg=W0201
        lineIndex = 0
        self.spectrumID = self.readIDline(lines[lineIndex])

        lineIndex += 1
        self.group, self.sample = self.readGroupSampleLine(lines[lineIndex])

        lineIndex += 1
        self.number, self.comment = self.readNumberCommentLine(lines[lineIndex])

        lineIndex += 1
        self.stageX, self.stageY, self.stageZ = self.readStageLine(lines[lineIndex])

        lineIndex += 1
        self.incidentEnergy_keV, self.probeDiameter, self.scanOn = self.readBeamLine(lines[lineIndex])

        lineIndex += 1
        self.date = self.readDateline(lines[lineIndex])

        lineIndex += 1
        self.detectorType, self.numberAccumulation = self.readDetectorLine(lines[lineIndex])

        lineIndex += 1

        lineIndex += 1
        self.current_A = self.readCurrentLine(lines[lineIndex])

        lineIndex += 1
        positions = self.getPositions(lines)

        self.elementData = {}

        start, end = positions['intensity']
        self.readIntensityLines(lines[start:end], self.elementData)

        start, end = positions['correction']
        self.readCorrectionLines(lines[start:end], self.elementData)

        start, end = positions['concentration']
        self.readConcentrationLines(lines[start:end], self.elementData)

        start, end = positions['total']
        self.readTotalLines(lines[start:end], self.elementData)

        return self.spectrumID

    def getValue(self, label, symbol=None):
        if symbol == None:
            if label == 'id':
                return self.spectrumID

            if label == 'group':
                return self.group

            if label == 'sample':
                return self.sample

            if label == 'number':
                return self.number

            if label == 'comment':
                return self.comment

            if label == 'stageX':
                return self.stageX

            if label == 'stageY':
                return self.stageY

            if label == 'stageZ':
                return self.stageZ

            if label == 'incidentEnergy_keV':
                return self.incidentEnergy_keV

            if label == 'probeDiameter':
                return self.probeDiameter

            if label == 'scanOn':
                return self.scanOn

            if label == 'date':
                return self.date

            if label == 'detectorType':
                return self.detectorType

            if label == 'numberAccumulation':
                return self.numberAccumulation

            if label == 'current_A':
                return self.current_A

        elif symbol in self.elementData:
            if symbol == 'total':
                if label in self.elementData['total']:
                    return self.elementData['total'][label]
            else:
                if label in self.elementData[symbol]:
                    return self.elementData[symbol][label]

        return 0.0

class JEOL8900McGill(object):
    def __init__(self, filename):
        self.points = None
        self.masterHeader = None

        self.readResultsFile(filename)

    def readResultsFile(self, filename):
        lines = open(filename, 'r').readlines()

        pointsIndex = []

        for line in lines:
            #line = line.strip()

            if 'Intensity' in line:
                self.readMasterHeader(line)

            if 'Unknown Specimen No.' in line:
                pointsIndex.append(lines.index(line))

            if len(line) == 0:
                #print line
                pass

        self.points = {}

        for index in pointsIndex:
            #print "Points:"
            #print lines[index:index+30]
            self.readPointData(lines[index:index+30])

        #print len(pointsIndex)

        return len(lines)

    def readPointData(self, lines):
        point = DataPoint()

        spectrumID = point.readLines(lines)

        self.points[spectrumID] = point

    def readMasterHeader(self, line):
        keywords = ['Intensity', 'Group', 'Sample', 'Page']

        positionKeywords = []

        for keyword in keywords:
            position = line.find(keyword)

            positionKeywords.append(position)

        self.masterHeader = {}

#        start = 0
#        for index,keyword in enumerate(keywords[:-1]):
#            end = positions[index+1]
#            values = line[start:end].split(':')

    def getValuesList(self, label, symbol=None):
        ids = self.points.keys()
        ids.sort()

        values = []

        for spectrumID in ids:
            if symbol == None:
                value = self.points[spectrumID].getValue(label)

                values.append(value)
            elif symbol != None:
                value = self.points[spectrumID].getValue(label, symbol)

                values.append(value)

        return ids, values

def run():
    filename = "/home/hdemers/works/results/experiments/epma/mcgill/data0407.ful"

    linescanFile = JEOL8900McGill(filename)

    keys = linescanFile.points.keys()
    keys.sort()

    print(keys, len(keys))

if __name__ == '__main__':  # pragma: no cover
    run()
