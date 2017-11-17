#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np


class Normalization:
    def __init__(self):
        self._beamline = None
        self._type = 'Monitor'
        self._range = 0, 0

    @property
    def beamline(self):
        return self._beamline

    @beamline.setter
    def beamline(self, beamline):
        self._beamline = beamline

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, t):
        self._type = t

    @property
    def range(self):
        return self._range

    @range.setter
    def range(self, r):
        self._range = 0, 0
        if isinstance(r, (tuple, list)):
            try:
                self._range = min(r), max(r)
            except TypeError:
                pass

    def __call__(self, img):
        if self._type == 'Monitor':
            try:
                return {
                    'Dubble': self._dubble_monitor_normalization,
                    'SNBL': self._snbl_monitor_normalization,
                }[self._beamline](img)
            except KeyError:
                pass
        return img

    def norm_after(self, res, calib):
        r1, r2 = self._range
        if self._type == 'Background' or self._type == 'Bkg' and r1 != r2:
            _min = np.abs(res - r1).argmin()
            _max = np.abs(res - r2).argmin()
            if not _min and not _max:
                n = res[1].sum()
            else:
                n = res[1, _min:_max].sum()
            if n > 0:
                res[1:] /= n / calib
        return res

    def _dubble_monitor_normalization(self, img):
        i1 = img.header.get('Monitor', 0)
        photo = img.header.get('Photo', 0)
        img.float()
        if i1 < 1:
            i1 = float(img.array.sum())
        if i1 > 1:
            img.array /= i1
            if photo:
                img.transmission = photo / i1
        img.photo = photo
        return img

    def _snbl_monitor_normalization(self, img, flux=None):
        img.float()
        flux = img.header.get('Flux') or flux
        if flux:
            img.array /= flux
        return img
