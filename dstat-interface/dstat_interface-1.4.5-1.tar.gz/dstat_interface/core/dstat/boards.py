#!/usr/bin/env python
# -*- coding: utf-8 -*-
#     DStat Interface - An interface for the open hardware DStat potentiostat
#     Copyright (C) 2017  Michael D. M. Dryden - 
#     Wheeler Microfluidics Laboratory <http://microfluidics.utoronto.ca>
#         
#     
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#     
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU General Public License for more details.
#     
#     You should have received a copy of the GNU General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import division, absolute_import, print_function, unicode_literals
import sys
import inspect
import logging

from pkg_resources import parse_version, parse_requirements

logger = logging.getLogger(__name__)


class BaseBoard(object):
    pcb_version = 'x.x.x'
    booster = False

    def __init__(self):
        self.max_freq = 5000
        self.max_scans = 255
        self.max_time = 65535

        self.setup()
        assert len(self.gain) == self.gain_settings
        assert len(self.gain_labels) == self.gain_settings
        if self.gain_trim is not None:
            assert len(self.gain_trim) == self.gain_settings

    def setup(self):
        """Override in subclasses to provide correct numbers"""
        self.gain = [1, 1e2, 3e3, 3e4, 3e5, 3e6, 3e7, 1e8]
        self.gain_labels = ["Bypass", "100 Ω (15 mA FS)", "3 kΩ (500 µA FS)",
                            "30 kΩ (50 µA FS)", "300 kΩ (5 µA FS)",
                            "3 MΩ (500 nA FS)", "30 MΩ (50 nA FS)",
                            "100 MΩ (15 nA FS)"
                           ]
        self.gain_trim = [None, 'r100_trim', 'r3k_trim',
                          'r30k_trim', 'r300k_trim', 'r3M_trim',
                          'r30M_trim', 'r100M_trim']
        self.gain_settings = len(self.gain)
        self.gain_default_index = 2
        self.re_voltage_scale = 1

    def test_mv(self, mv):
        """Return true if voltage in mV is in range."""
        dac = float(mv)*self.re_voltage_scale/(3000./65536) + 32768

        if 0 <= dac <= 65535:
            return True
        else:
            return False

    def test_freq(self, hz):
        """Return true if frequency in Hz is in range."""
        return 0 < float(hz) < self.max_freq

    def test_scans(self, n):
        """Return true if number of scans is valid."""
        return 0 < int(n) < self.max_scans

    def test_s(self, s):
        """Return true if time in integer seconds is valid."""
        return 0 < int(s) < self.max_time


class V1_1Board(BaseBoard):
    pcb_version = '1.1'

    def setup(self):
        self.gain = [1e2, 3e2, 3e3, 3e4, 3e5, 3e6, 3e7, 5e8]
        self.gain_labels = [None, "300 Ω (5 mA FS)",
                            "3 kΩ (500 µA FS)", "30 kΩ (50 µA FS)",
                            "300 kΩ (5 µA FS)", "3 MΩ (500 nA FS)",
                            "30 MΩ (50 nA FS)", "500 MΩ (3 nA FS)"
                            ]
        self.gain_trim = None
        self.gain_settings = len(self.gain)
        self.gain_default_index = 2
        self.re_voltage_scale = 1


class V1_2Board(BaseBoard):
    pcb_version = '1.2'

    def setup(self):
        self.gain = [1, 1e2, 3e3, 3e4, 3e5, 3e6, 3e7, 1e8]
        self.gain_labels = ["Bypass", "100 Ω (15 mA FS)", "3 kΩ (500 µA FS)",
                            "30 kΩ (50 µA FS)", "300 kΩ (5 µA FS)",
                            "3 MΩ (500 nA FS)", "30 MΩ (50 nA FS)",
                            "100 MΩ (15 nA FS)"
                           ]
        self.gain_trim = [None, 'r100_trim', 'r3k_trim',
                          'r30k_trim', 'r300k_trim', 'r3M_trim',
                          'r30M_trim', 'r100M_trim']
        self.gain_settings = len(self.gain)
        self.gain_default_index = 2
        self.re_voltage_scale = 1


def __get_all_subclasses(cls):
    all_subclasses = []

    for subclass in cls.__subclasses__():
        all_subclasses.append(subclass)
        all_subclasses.extend(__get_all_subclasses(subclass))

    return all_subclasses


def find_board(version, booster=False):
    """Returns highest compatible board class or None if none available."""
    boards = __get_all_subclasses(BaseBoard)
    candidates = []
    for board in boards:
        req = parse_requirements('dstat~={}'.format(board.pcb_version)).next()
        if board.booster == booster and version in req:
            candidates.append(board)
    try:
        picked = sorted(candidates,
                        key=lambda board: parse_version(board.pcb_version))[-1]
        logger.info("Picked %s", picked)
        return picked
    except IndexError:
        logger.warning("No matching board definition for ver: %s.", version)
        return None
