#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import binascii
import numpy as np
import cryio
from .beamline import correctMask


class Mask:
    def __init__(self):
        self._mask = None
        self._mask_checksum = 0
        self._beamline = ''
        self._type = ''
        self._mask_mtime = 0

    def init(self, mask, beamline, typ):
        if isinstance(mask, str) and mask:
            checksum = binascii.crc32(mask.encode())
            res = checksum == self._mask_checksum
            self._mask_checksum = checksum
            mtime = os.path.getmtime(mask)
            if res and self._beamline == beamline and self._type == typ and mtime <= self._mask_mtime:
                return
            try:
                self._mask = cryio.openImage(mask)
            except (IOError, cryio.fit2dmask.NotFit2dMask, cryio.numpymask.NotNumpyMask):
                self._mask = None
            else:
                self._mask = correctMask(beamline, typ, self._mask).array
                self._mask[self._mask == 1] = -1
            self._beamline = beamline
            self._type = typ
            self._mask_mtime = mtime
        elif isinstance(mask, np.ndarray):
            self._mask_checksum = ''
            self._beamline = ''
            self._type = ''
            self._mask_mtime = 0
            if mask is self._mask:
                return
            self._mask = mask
        else:
            self._mask = None
            self._mask_checksum = 0
            self._beamline = ''
            self._type = ''
            self._mask_mtime = 0

    def __call__(self, image):
        if self._mask is not None and image.array.shape == self._mask.shape:
            image.array = np.where(self._mask == -1, self._mask, image.array)
        return image
