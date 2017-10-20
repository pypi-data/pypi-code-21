#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import threading
import numpy as np
from . import poni, utils


class IGracio:
    __units = {'t': 0, 'q': 1}

    def __init__(self, *, precision='float'):
        self._precision = precision
        self._c_type = utils.type_by_precision(precision)
        self._i = None
        self.pos = None
        self._poni = None
        self._poni_checksum = 0
        self._units = 't'
        self._azimuth = 0, 0
        self._radial = 0, 0
        self._bins = 0
        self._polarization = -2
        self.__lock = threading.RLock()
        self.dim1 = 0
        self.dim2 = 0

    @property
    def precision(self):
        return self._precision

    def _check_poni_checksum(self, poni_text):
        checksum = binascii.crc32(poni_text.encode())
        res = checksum == self._poni_checksum
        self._poni_checksum = checksum
        return res

    @property
    def poni(self):
        return self._poni

    @poni.setter
    def poni(self, poni_text):
        with self.__lock:
            if not self._check_poni_checksum(poni_text):
                self._poni = poni.Poni(poni_text, precision=self._precision)
                self._i = None

    def _initialization(self, shape):
        with self.__lock:
            if self._poni is None:
                raise utils.IntegracioError('Poni is not initialized')
            if (self.dim1, self.dim2) != shape:
                self.dim1, self.dim2 = shape
                self._i = None
            if self._i is None:
                self._poni.units = self.__units.get(self._units, 0)
                self._poni.radial = self._radial
                self._poni.bins = self._bins
                self._poni.polarization = self._polarization
                self._i = utils.integration(self._precision)(self.dim1, self.dim2, self._poni.geometry())
                self.pos = np.asarray(self._i)

    def _integrate(self, image, azmin, azmax):
        image = image if isinstance(image, np.ndarray) else image.array
        self._initialization(image.shape)
        if azmin is None and azmax is None:
            azmin, azmax = self._azimuth
        results = np.asarray(utils.results(self._precision)(self._i, image.astype(self._c_type), azmin, azmax))
        return self.pos, results[0], results[1]

    def __call__(self, image, azmin=None, azmax=None):
        # if we integrate by azimuthal slices (oh, god), then the azimuth property does not work :(
        return self._integrate(image, azmin, azmax)

    @property
    def units(self):
        return self._units

    @units.setter
    def units(self, units):
        with self.__lock:
            if units != self._units:
                self._units = units
                self._i = None

    @property
    def azimuth(self):
        return self._azimuth

    @azimuth.setter
    def azimuth(self, azimuth):
        if azimuth is None:
            azimuth = 0, 0
        with self.__lock:
            if self._azimuth != azimuth:
                self._azimuth = azimuth

    @property
    def radial(self):
        return self._radial

    @radial.setter
    def radial(self, radial):
        if radial is None:
            radial = 0, 0
        with self.__lock:
            if self._radial != radial:
                self._radial = radial
                self._i = None

    @property
    def sa(self):
        return self._poni.sa

    @sa.setter
    def sa(self, use: bool):
        with self.__lock:
            self._poni.sa = use

    @property
    def bins(self):
        return self._bins

    @bins.setter
    def bins(self, bins: int):
        with self.__lock:
            if bins != self._bins:
                self._bins = bins
                self._i = None

    @property
    def polarization(self):
        return self._polarization

    @polarization.setter
    def polarization(self, factor: float):
        with self.__lock:
            if factor != self._polarization:
                self._polarization = factor
                self._i = None
