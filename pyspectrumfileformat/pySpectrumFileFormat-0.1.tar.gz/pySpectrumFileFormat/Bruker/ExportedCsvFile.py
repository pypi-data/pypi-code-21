#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. py:currentmodule:: Bruker.ExportedCsvFile
   :synopsis: Read exported bruker csv file.

.. moduleauthor:: Hendrix Demers <hendrix.demers@mail.mcgill.ca>

Read exported bruker csv file.
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
import csv

# Third party modules.

# Local modules.

# Project modules.

# Globals and constants variables.

KEY_ENERGY = "Primary energy: "
KEY_LIFETIME = "Life time: "
KEY_SPECTRUM = "Spectrum: "
KEY_CHANNEL = "Channel"

class Spectrum(object):
    def __init__(self):
        self.spectrumName = ""
        self.primaryEnergy_keV = 0.0
        self.lifeTime_s = 0.0

        self.channels = []
        self.energies_keV = []
        self.countsList = []

    @property
    def spectrumName(self):
        return self._spectrumName
    @spectrumName.setter
    def spectrumName(self, spectrumName):
        self._spectrumName = spectrumName

    @property
    def primaryEnergy_keV(self):
        return self._primaryEnergy_keV
    @primaryEnergy_keV.setter
    def primaryEnergy_keV(self, primaryEnergy_keV):
        self._primaryEnergy_keV = primaryEnergy_keV

    @property
    def lifeTime_s(self):
        return self._lifeTime_s
    @lifeTime_s.setter
    def lifeTime_s(self, lifeTime_s):
        self._lifeTime_s = lifeTime_s

    @property
    def channels(self):
        return self._channels
    @channels.setter
    def channels(self, channels):
        self._channels = channels

    @property
    def energies_keV(self):
        return self._energies_keV
    @energies_keV.setter
    def energies_keV(self, energies_keV):
        self._energies_keV = energies_keV

    @property
    def countsList(self):
        return self._countsList
    @countsList.setter
    def countsList(self, countsList):
        self._countsList = countsList

def readSpectrum(filepath):
    logging.info("Reading spectrum: %s", filepath)

    reader = csv.reader(open(filepath, 'rb'))

    spectrum = Spectrum()

    for row in reader:
        if row[0] == KEY_SPECTRUM:
            spectrum.spectrumName = row[1].strip()

        if row[0] == KEY_ENERGY:
            spectrum.primaryEnergy_keV = float(row[2])

        if row[0] == KEY_LIFETIME:
            if row[3] == "ms":
                spectrum.lifeTime_s = float(row[2])*1.0e-3

        if row[0] == KEY_CHANNEL:
            break

    for row in reader:
        channel = int(row[0])
        energy_keV = float(row[1])
        counts = float(row[2])

        spectrum.channels.append(channel)
        spectrum.energies_keV.append(energy_keV)
        spectrum.countsList.append(counts)

    assert len(spectrum.channels) == len(spectrum.energies_keV)
    assert len(spectrum.channels) == len(spectrum.countsList)

    logging.info(spectrum.spectrumName)
    logging.info(spectrum.primaryEnergy_keV)
    logging.info(spectrum.lifeTime_s)
    logging.info(len(spectrum.channels))

    return spectrum
