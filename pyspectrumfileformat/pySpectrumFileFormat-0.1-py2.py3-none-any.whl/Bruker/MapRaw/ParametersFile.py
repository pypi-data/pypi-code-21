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
DATA_TYPE_UNSIGNED = "unsigned"
DATA_TYPE_SIGNED = "signed"

BYTE_ORDER_DONT_CARE = "dont-care"
BYTE_ORDER_LITTLE_ENDIAN = "little-endian"

RECORED_BY_IMAGE = "image"
RECORED_BY_VECTOR = "vector"

KEY_WIDTH = "width"
KEY_HEIGHT = "height"
KEY_DEPTH = "depth"
KEY_OFFSET = "offset"
KEY_DATA_LENGTH_B = "data-length"
KEY_DATA_TYPE = "data-type"
KEY_BYTE_ORDER = "byte-order"
KEY_RECORED_BY = "record-by"
KEY_ENERGY_keV = "E0_kV"
KEY_PIXEL_SIZE_nm = "px_size_nm"

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
        self.energy_keV = None
        self.pixel_size_nm = None

    def read(self, filepath):
        logging.info("Reading parameters file: %s", filepath)

        lines = open(filepath, 'r').readlines()

        for line in lines:
            line = line.replace('(', '').replace(')', '')
            line = line.lower()

            keywords = self._getKeywords()
            valueFormatters = self._getValueFormatter()
            for keyword in keywords:
                if keyword.lower() in line:
                    line = line.strip()
                    value = line.replace(keyword.lower(), '').replace("mlx::", '').replace(":", '')
                    valueFormatter = valueFormatters[keyword]
                    self._parameters[keyword] = valueFormatter(value)

    def write(self, filepath):
        logging.info("Writing parameters file: %s", filepath)

        with open(filepath, 'w', newline='\n') as output_file:
            lines = []
            keywords = self._getKeywords()
            for keyword in keywords:
                line = "%12s \t %s\n" % (keyword, self._parameters[keyword])
                lines.append(line)

            output_file.writelines(lines)

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
        keywords.append(KEY_ENERGY_keV)
        keywords.append(KEY_PIXEL_SIZE_nm)

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
        valueFormatters[KEY_RECORED_BY] = self._extractRecordBy
        valueFormatters[KEY_ENERGY_keV] = float
        valueFormatters[KEY_PIXEL_SIZE_nm] = float

        return valueFormatters

    def _extractDataType(self, valueStr):
        valueStr = valueStr.strip().lower()

        if valueStr == DATA_TYPE_UNSIGNED:
            return DATA_TYPE_UNSIGNED
        elif valueStr == DATA_TYPE_SIGNED:
            return DATA_TYPE_SIGNED

    def _extractByteOrder(self, valueStr):
        valueStr = valueStr.strip().lower()

        if valueStr == BYTE_ORDER_DONT_CARE:
            return BYTE_ORDER_DONT_CARE
        elif valueStr == BYTE_ORDER_LITTLE_ENDIAN:
            return BYTE_ORDER_LITTLE_ENDIAN

    def _extractString(self, valueStr):
        return valueStr.strip()

    def _extractRecordBy(self, valueStr):
        if RECORED_BY_IMAGE in valueStr:
            return RECORED_BY_IMAGE
        elif RECORED_BY_VECTOR in valueStr:
            return RECORED_BY_VECTOR

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

    @property
    def energy_keV(self):
        return self._parameters[KEY_ENERGY_keV]
    @energy_keV.setter
    def energy_keV(self, energy_keV):
        self._parameters[KEY_ENERGY_keV] = energy_keV

    @property
    def pixel_size_nm(self):
        return self._parameters[KEY_PIXEL_SIZE_nm]
    @pixel_size_nm.setter
    def pixel_size_nm(self, pixel_size_nm):
        self._parameters[KEY_PIXEL_SIZE_nm] = pixel_size_nm
