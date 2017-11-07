#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: pySpectrumFileFormat.OxfordInstruments.INCA.ReadSpectrumProcessingResults
   :synopsis: Read Oxford Instrument spectrum processing result file from INCA.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read Oxford Instrument spectrum processing result file from INCA.
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

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.

class ReadSpectrumProcessingResults(object):
    _HEADERSTRING = "Fit index"

    def __init__(self, filepath):
        self.data = {}

        self.read(filepath)

        if len(self.data) == 0:
            raise ValueError

    def read(self, filepath):
        lines = open(filepath, 'r').readlines()

        self._extractData(lines)

    def _extractData(self, lines):
        if self._HEADERSTRING not in lines[0]:
            raise ValueError

        data = {}

        line = lines[0].strip()
        headers = line.split("\t")

        for line in lines[1:]:
            line = line.strip()

            if len(line) == 0:
                continue

            items = line.split("\t")

            if len(items) == 6:
                for index,item in enumerate(items[:3]):
                    data.setdefault(headers[index], []).append(item)

                for index,item in enumerate(items[3:]):
                    try:
                        data.setdefault(headers[index+3], []).append(float(item))
                    except ValueError:
                        data.setdefault(headers[index+3], []).append(0.0)

            elif len(items) == 5:
                data.setdefault(headers[0], []).append("")

                for index,item in enumerate(items[:2]):
                    data.setdefault(headers[index+1], []).append(item)

                for index,item in enumerate(items[2:]):
                    try:
                        data.setdefault(headers[index+3], []).append(float(item))
                    except ValueError:
                        data.setdefault(headers[index+3], []).append(0.0)

        self.data = data
        self.headers = headers

def isValidFile(filepath):
    isValid = False

    try:
        ReadSpectrumProcessingResults(filepath)

        isValid = True
    except ValueError:
        isValid = False

    return isValid
