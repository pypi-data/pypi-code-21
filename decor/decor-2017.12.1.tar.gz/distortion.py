#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import threading
import numpy as np
from .spline import Spline
from . import _decor


class Distortion:
    def __init__(self):
        self._dist = None
        self._lock = threading.Lock()
        self.spline = None
        self.spline_file = None
        self.shape = None
        self._spline_checksum = 0

    def init(self, spline):
        with self._lock:
            if spline:
                checksum = binascii.crc32(spline.encode())
                res = checksum == self._spline_checksum
                self._spline_checksum = checksum
                if not res:
                    self.spline_file = spline
                    self.spline = Spline(spline)
                    self._dist = None
            else:
                self._spline_checksum = 0
                self._dist = None
                self.shape = None
                self.spline_file = None
                self.spline = None

    def __call__(self, image):
        return self._correct(image if isinstance(image, np.ndarray) else image.array)

    def _correct(self, image):
        with self._lock:
            if image.shape != self.shape:
                self.shape = image.shape
                self._dist = None
            if self.spline and not self._dist:
                self._init_lut()
        if not self._dist:
            return image
        return np.asarray(_decor._distortion_cor(self._dist, image.ravel().astype(np.float32)))

    def calc_cartesian_positions(self, d1, d2):
        d1c = d1 + 0.5
        d2c = d2 + 0.5
        dx = self.spline.func_x_y(d2c, d1c, 0)
        dy = self.spline.func_x_y(d2c, d1c, 1)
        return dy + d1c, dx + d2c

    def _init_lut(self):
        dim1, dim2 = self.shape
        pos_corners = np.empty((dim1+1, dim2+1, 2), dtype=np.float64)
        d1 = np.outer(np.arange(dim1+1, dtype=np.float64), np.ones(dim2+1, dtype=np.float64)) - 0.5
        d2 = np.outer(np.ones(dim1+1, dtype=np.float64), np.arange(dim2+1, dtype=np.float64)) - 0.5
        pos_corners[:, :, 0], pos_corners[:, :, 1] = self.calc_cartesian_positions(d1, d2)
        pos = np.empty((dim1, dim2, 4, 2), dtype=np.float32)
        pos[:, :, 0, :] = pos_corners[:-1, :-1]
        pos[:, :, 1, :] = pos_corners[:-1, 1:]
        pos[:, :, 2, :] = pos_corners[1:, 1:]
        pos[:, :, 3, :] = pos_corners[1:, :-1]
        delta0 = int((np.ceil(pos_corners[1:, :, 0]) - np.floor(pos_corners[:-1, :, 0])).max())
        delta1 = int((np.ceil(pos_corners[:, 1:, 1]) - np.floor(pos_corners[:, :-1, 1])).max())
        self._dist = _decor._distortion(dim1, dim2, delta0, delta1, pos)
