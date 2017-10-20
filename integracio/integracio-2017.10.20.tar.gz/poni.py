#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
from .utils import PoniError, geometry_by_precision


class Poni:
    KEYS = 'pixelsize1', 'pixelsize2', 'distance', 'poni1', 'poni2', 'rot1', 'rot2', 'rot3', 'wavelength'

    def __init__(self, poni_text, *, precision='float'):
        self._poni_text = poni_text
        self._data = {}
        self._geometry = None
        self._beamx = None
        self._beamy = None
        self._t1 = None
        self._t2 = None
        self._t3 = None
        self._t4 = None
        self._tilt = None
        self._dd = None
        self._tpr = None
        self._geometry_struct = geometry_by_precision(precision)
        self._read()
        self._parse()

    def _read(self):
        for i, line in enumerate(self._poni_text.splitlines()):
            if line.startswith('#') or ':' not in line:
                continue
            words = line.split(':', 1)
            key = words[0].strip().lower()
            try:
                value = words[1].strip()
            except IndexError:
                raise PoniError(f'Line {i} of poni file seems to be corrupted')
            else:
                self._data[key] = value

    def _parse(self):
        for key in Poni.KEYS:
            value = self._data.get(key, 0)
            if value:
                try:
                    value = float(value)
                except ValueError:
                    raise PoniError(f'The poni file seems to be corrupted, the key "{key}" -> "{value}" cannot be read')
                else:
                    self._data[key] = value
                    self.__dict__[key] = value
            else:
                raise PoniError(f'The poni file seems to be invalid, it does not contain key "{key}"')
        self._geometry = self._geometry_struct(**self._data)
        self._geometry.units = 0
        self._geometry.radmin = 0
        self._geometry.radmax = 0
        self._geometry.sa = 1
        self._geometry.bins = 0
        self._geometry.pol = -2

    def geometry(self):
        return self._geometry

    @property
    def units(self):
        return self._geometry.units

    @units.setter
    def units(self, units):
        self._geometry.units = units

    @property
    def wavelength(self):
        return self._geometry.wavelength * 1e10

    @wavelength.setter
    def wavelength(self, wl):
        self._geometry.wavelength = wl * 1e-10

    @property
    def radial(self):
        return self._geometry.radmin, self._geometry.radmax

    @radial.setter
    def radial(self, radial):
        if radial is None:
            radial = 0, 0
        self._geometry.radmin, self._geometry.radmax = radial

    @property
    def poni1(self):
        return self._geometry.poni1

    @property
    def poni2(self):
        return self._geometry.poni2

    @property
    def __t1(self):
        if self._t1 is None:
            self._t1 = math.cos(self.rot1) * math.cos(self.rot2)
        return self._t1

    @property
    def __t2(self):
        if self._t2 is None:
            self._t2 = math.sqrt(1 - self.__t1 ** 2)
        return self._t2

    @property
    def __t3(self):
        if self._t3 is None:
            if self.__t2:
                # noinspection PyTypeChecker
                self._t3 = max(-1, min(1, -math.cos(self.rot2) * math.sin(self.rot1) / self.__t2))
            else:
                self._t3 = 1
        return self._t3

    @property
    def __t4(self):
        if self._t4 is None:
            if self.__t2:
                self._t4 = math.sin(self.rot2) / self.__t2
            else:
                self._t4 = 0
        return self._t4

    @property
    def beamx(self):
        if self._beamx is None:
            # Copied from pyFAI
            self._beamx = (self.poni2 + self.distance * self.__t2 / self.__t1 * self.__t3) / self.pixel2
        return self._beamx

    @property
    def beamy(self):
        if self._beamy is None:
            # Copied from pyFAI
            if abs(self.tilt) < 1e-5:
                self._beamy = self.poni1 / self.pixel1
            else:
                self._beamy = (self.poni1 + self.distance * self.__t2 / self.__t1 * self.__t4) / self.pixel1
        return self._beamy

    @property
    def pixel1(self):
        return self._geometry.pixelsize1

    @property
    def pixel2(self):
        return self._geometry.pixelsize2

    @property
    def distance(self):
        return self._geometry.distance

    @property
    def rot1(self):
        return self._geometry.rot1

    @property
    def rot2(self):
        return self._geometry.rot2

    @property
    def rot3(self):
        return self._geometry.rot3

    @property
    def tilt(self):
        if self._tilt is None:
            self._tilt = math.degrees(math.acos(self.__t1))
        return self._tilt

    @property
    def direct_distance(self):
        if self._dd is None:
            self._dd = 1e3 * self.distance / self.__t1
        return self._dd

    @property
    def tilt_plan_rotation(self):
        if self._tpr is None:
            self._tpr = math.copysign(math.degrees(math.acos(self.__t3)), self.__t4)
        return self._tpr

    @staticmethod
    def open(filename):
        with open(filename, 'r') as poni_text:
            return Poni(poni_text.read())

    @property
    def sa(self):
        return self._geometry.sa

    @sa.setter
    def sa(self, use: bool):
        self._geometry.sa = int(use)

    @property
    def bins(self):
        return self._geometry.bins

    @bins.setter
    def bins(self, bins: int):
        self._geometry.bins = bins

    @property
    def polarization(self):
        return self._geometry.pol

    @polarization.setter
    def polarization(self, factor: float):
        self._geometry.pol = factor
