#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Adam.Dybbroe

# Author(s):

#   Adam.Dybbroe <a000680@c20671.ad.smhi.se>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
"""


from pyspectral.rsr_reader import RelativeSpectralResponse
from pyspectral.solar import (
    SolarIrradianceSpectrum, TOTAL_IRRADIANCE_SPECTRUM_2000ASTM)
modis = RelativeSpectralResponse('EOS-Aqua', 'modis')
solar_irr = SolarIrradianceSpectrum(
    TOTAL_IRRADIANCE_SPECTRUM_2000ASTM, dlambda=0.005)
sflux = solar_irr.inband_solarflux(modis.rsr['20'])
print("Solar flux over Band: ", round(sflux, 6))

from pyspectral.near_infrared_reflectance import Calculator
sunz = 80.
tb3 = 290.0
tb4 = 282.0
refl37 = Calculator(
    'Sentinel-3A', 'slstr', 3.8, detector='det-1', solar_flux=2.0029281634299041)
print round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)

refl37 = Calculator(
    'EOS-Aqua', 'modis', '20', detector='det-1', solar_flux=2.0029281634299041)
print round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)

# refl37 = Calculator(
#     'EOS-Aqua', 'modis', 3.7, detector='det-1', solar_flux=2.0029281634299041)
# print round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)
# refl37 = Calculator(
#     'EOS-Aqua', 'modis', 4.0, detector='det-1', solar_flux=2.0029281634299041)
# print round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)
# refl37 = Calculator(
#     'EOS-Aqua', 'modis', 5.0, detector='det-1', solar_flux=2.0029281634299041)
# print round(refl37.reflectance_from_tbs(sunz, tb3, tb4), 6)
