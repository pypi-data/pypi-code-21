#!/usr/bin/env python
# -*- coding: utf-8 -*-

import binascii
import cryio


class FloodField:
    def __init__(self):
        self._flat = None
        self._flat_checksum = 0

    def init(self, flat=None):
        if not flat:
            self._flat = None
            self._flat_checksum = 0
            return
        checksum = binascii.crc32(flat.encode())
        res = checksum == self._flat_checksum
        self._flat_checksum = checksum
        if res:
            return
        self._flat = cryio.openImage(flat)
        self._flat.float()

    def __call__(self, image):
        if self._flat is not None:
            array = image.array if hasattr(image, 'array') else image
            if array.shape == self._flat.array.shape:
                array /= self._flat.array
        return image
