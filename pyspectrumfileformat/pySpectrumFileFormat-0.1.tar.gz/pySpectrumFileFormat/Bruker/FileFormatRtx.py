#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: Bruker.FileFormatRtx
   :synopsis: Read EDS Esprit file format rtx.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read EDS Esprit file format rtx.
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
import zlib
import base64
import logging
from xml.etree.ElementTree import ElementTree, XML

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.
TAG_HEADER = "RTHeader"
TAG_DATA = "RTData"
TAG_PROJECT_HEADER = "ProjectHeader"
TAG_COMPRESSION = "RTCompression"
TAG_DATE = "Date"
TAG_TIME = "Time"
TAG_CREATOR = "Creator"
TAG_COMMENT = "Comment"

class FileFormatRtx(object):
    def __init__(self):
        self._etree = ElementTree()

    def readFile(self, filepath):
        self._etree = ElementTree(file=filepath)

        logging.info("Root: %s", self._etree.getroot())

        root = self._etree.getroot()

        #for element in etree.getiterator():
        for element in root.getchildren():
            logging.debug("tag: %s", element.tag)
            logging.debug("    %s", element.text)
            #logging.debug("    %s", element.tail)
            logging.debug("    %s", element.attrib)

    def printHeader(self):
        headerElements = self.getHeaderElements()

        for element in headerElements:
            self._printElement(element)

    def getHeaderElements(self):
        parentElement =  self._etree.find(TAG_HEADER)
        elements = parentElement.getchildren()

        return elements

    def printProjectHeader(self):
        elements = self.getProjectHeaderElements()

        for element in elements:
            self._printElement(element)

    def getProjectHeaderElements(self):
        parentElement =  self._etree.find("*//"+TAG_PROJECT_HEADER)
        elements = parentElement.getchildren()

        return elements

    def printCompression(self):
        element = self.getCompressionElement()

        self._printElement(element)

    def getCompressionElement(self):
        parentElement =  self._etree.find("*//"+TAG_COMPRESSION)

        return parentElement

    def printDate(self):
        element = self.getDateElement()

        self._printElement(element)

    def getDateElement(self):
        parentElement =  self._etree.find("*//"+TAG_DATE)

        return parentElement

    def printTime(self):
        element = self.getTimeElement()

        self._printElement(element)

    def getTimeElement(self):
        parentElement =  self._etree.find("*//"+TAG_TIME)

        return parentElement

    def printCreator(self):
        element = self.getCreatorElement()

        self._printElement(element)

    def getCreatorElement(self):
        parentElement =  self._etree.find("*//"+TAG_CREATOR)

        return parentElement

    def printComment(self):
        element = self.getCommentElement()

        self._printElement(element)

    def getCommentElement(self):
        parentElement =  self._etree.find("*//"+TAG_COMMENT)

        return parentElement

    def decompress(self, compressedData):
        compressedData = base64.b64decode(compressedData)
        data = zlib.decompress(compressedData)

        return data

    def extractData(self, data):
        etree = XML(data)

        logging.info("Root: %s", etree.getroot())

    def _printElement(self, element):
        logging.info("tag: %s", element.tag)
        logging.info("    %s", element.text)
        #logging.info("    %s", element.tail)
        logging.info("    %s", element.attrib)

def runData():
    import os.path

    path = r"../testData/Bruker"
    filename = "CN.zlib"
    compressedDataFilepath = os.path.join(path, filename)

    compressedData = open(compressedDataFilepath, 'rb').readlines()[0]

    fileFormatRtx = FileFormatRtx()

    data = fileFormatRtx.decompress(compressedData)
    fileFormatRtx.extractData(data)

    print(data)

    path = r"../testData/Bruker"
    filename = "CN.dat"
    decompressedDataFilepath = os.path.join(path, filename)

    decompressedDataFile = open(decompressedDataFilepath, 'wb')
    decompressedDataFile.write(data)

def runRTX():
    import os.path

    path = r"../testData/Bruker"
    filename = "CN.rtx"
    filepath = os.path.join(path, filename)
    fileFormatRtx = FileFormatRtx()

    fileFormatRtx.readFile(filepath)

    #fileFormatRtx.printHeader()
    #fileFormatRtx.printProjectHeader()
    fileFormatRtx.printCompression()
    fileFormatRtx.printDate()
    fileFormatRtx.printTime()
    fileFormatRtx.printCreator()
    fileFormatRtx.printComment()

    #path = r"../testData/Bruker"
    #filename = "CN.dat"
    #decompressedDataFilepath = os.path.join(path, filename)

    #decompressedDataFile = open(decompressedDataFilepath, 'wb')
    #decompressedDataFile.write(data)


if __name__ == '__main__':  # pragma: no cover
    runRTX()
