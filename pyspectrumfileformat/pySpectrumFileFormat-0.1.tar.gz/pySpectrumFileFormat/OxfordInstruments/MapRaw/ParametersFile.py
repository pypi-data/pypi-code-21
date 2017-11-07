#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: OxfordInstruments.MapRaw.ParametersFile
   :synopsis: Parameters of the raw map file.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Parameters of the raw map file.
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
import logging

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.
DATA_TYPE_UNSIGNED = "UNSIGNED"
DATA_TYPE_SIGNED = "SIGNED"

BYTE_ORDER_DONT_CARE = "DONT-CARE"
BYTE_ORDER_LITTLE_ENDIAN = "LITTLE-ENDIAN"

KEY_WIDTH = "MLX::WIDTH"
KEY_HEIGHT = "MLX::HEIGHT"
KEY_DEPTH = "MLX::DEPTH"
KEY_OFFSET = "MLX::OFFSET"
KEY_DATA_LENGTH_B = "MLX::DATA-LENGTH"
KEY_DATA_TYPE = "MLX::DATA-TYPE :"
KEY_BYTE_ORDER = "MLX::BYTE-ORDER :"
KEY_RECORED_BY = "MLX::RECORD-BY :"

class ParametersFile(object):
    def __init__(self):
        self._parameters = {}

        self.width = None
        self.height = None
        self.depth = None
        self.offset = None
        self.dataLength_B = None
        self.dataType = None
        self.byteOrder = None
        self.recordBy = ""

    def read(self, filepath):
        logging.info("Reading parameters file: %s", filepath)

        lines = open(filepath, 'r').readlines()

        for line in lines:
            line = line.replace('(', '').replace(')', '')

            keywords = self._getKeywords()
            valueFormatters = self._getValueFormatter()
            for keyword in keywords:
                if keyword in line:
                    value = line.replace(keyword, '')
                    valueFormatter = valueFormatters[keyword]
                    self._parameters[keyword] = valueFormatter(value)

    def _getKeywords(self):
        keywords = []

        keywords.append(KEY_WIDTH)
        keywords.append(KEY_HEIGHT)
        keywords.append(KEY_DEPTH)
        keywords.append(KEY_OFFSET)
        keywords.append(KEY_DATA_LENGTH_B)
        keywords.append(KEY_DATA_TYPE)
        keywords.append(KEY_BYTE_ORDER)
        keywords.append(KEY_RECORED_BY)

        return keywords

    def _getValueFormatter(self):
        valueFormatters = {}

        valueFormatters[KEY_WIDTH] = int
        valueFormatters[KEY_HEIGHT] = int
        valueFormatters[KEY_DEPTH] = int
        valueFormatters[KEY_OFFSET] = int
        valueFormatters[KEY_DATA_LENGTH_B] = int
        valueFormatters[KEY_DATA_TYPE] = self._extractDataType
        valueFormatters[KEY_BYTE_ORDER] = self._extractByteOrder
        valueFormatters[KEY_RECORED_BY] = self._extractString

        return valueFormatters

    def _extractDataType(self, valueStr):
        valueStr = valueStr.strip().upper()

        if valueStr == DATA_TYPE_UNSIGNED:
            return DATA_TYPE_UNSIGNED
        elif valueStr == DATA_TYPE_SIGNED:
            return DATA_TYPE_SIGNED

    def _extractByteOrder(self, valueStr):
        valueStr = valueStr.strip().upper()

        if valueStr == BYTE_ORDER_DONT_CARE:
            return BYTE_ORDER_DONT_CARE
        elif valueStr == BYTE_ORDER_LITTLE_ENDIAN:
            return BYTE_ORDER_LITTLE_ENDIAN

    def _extractString(self, valueStr):
        return valueStr.strip()

    @property
    def width(self):
        return self._parameters[KEY_WIDTH]
    @width.setter
    def width(self, width):
        self._parameters[KEY_WIDTH] = width

    @property
    def height(self):
        return self._parameters[KEY_HEIGHT]
    @height.setter
    def height(self, height):
        self._parameters[KEY_HEIGHT] = height

    @property
    def depth(self):
        return self._parameters[KEY_DEPTH]
    @depth.setter
    def depth(self, depth):
        self._parameters[KEY_DEPTH] = depth

    @property
    def offset(self):
        return self._parameters[KEY_OFFSET]
    @offset.setter
    def offset(self, offset):
        self._parameters[KEY_OFFSET] = offset

    @property
    def dataLength_B(self):
        return self._parameters[KEY_DATA_LENGTH_B]
    @dataLength_B.setter
    def dataLength_B(self, dataLength_B):
        self._parameters[KEY_DATA_LENGTH_B] = dataLength_B

    @property
    def dataType(self):
        return self._parameters[KEY_DATA_TYPE]
    @dataType.setter
    def dataType(self, dataType):
        self._parameters[KEY_DATA_TYPE] = dataType

    @property
    def byteOrder(self):
        return self._parameters[KEY_BYTE_ORDER]
    @byteOrder.setter
    def byteOrder(self, byteOrder):
        self._parameters[KEY_BYTE_ORDER] = byteOrder

    @property
    def recordBy(self):
        return self._parameters[KEY_RECORED_BY]
    @recordBy.setter
    def recordBy(self, recordBy):
        self._parameters[KEY_RECORED_BY] = recordBy
