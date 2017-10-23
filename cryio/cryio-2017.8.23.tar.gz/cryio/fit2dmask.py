#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Fork of fabio fit2d mask reader
"""

import numpy as np
from .cryioimage import ImageError, CryioImage


class NotFit2dMask(ImageError):
    pass


class Fit2DMask(CryioImage):
    HEADER_ID = ('M', 0), ('A', 4), ('S', 8), ('K', 12)
    HEADER_SIZE = 1024
    Extensions = '.msk',

    def __init__(self, filepath=None):
        super().__init__(filepath)
        if self.filepath:
            self.parse()

    def parse(self):
        _map = open(self.filepath, 'rb')
        self.parse_header(_map)
        self.parse_body(_map)
        _map.close()

    def parse_header(self, _map):
        header = _map.read(self.HEADER_SIZE)
        for i, j in self.HEADER_ID:
            c = chr(header[j])
            if c != i:
                raise NotFit2dMask(f'Not a fit2d mask file {self.filepath}')
        fit2dhdr = np.fromstring(header, np.int32)
        self.dim1 = fit2dhdr[4]
        self.dim2 = fit2dhdr[5]

    def parse_body(self, _map):
        num_ints = (self.dim1 + 31) // 32
        total = self.dim2 * num_ints * 4
        data = _map.read(total)
        data = np.fromstring(data, np.uint8).reshape((self.dim2, num_ints * 4))
        # noinspection PyNoneFunctionAssignment
        result = np.empty((self.dim2, num_ints * 4 * 8), np.uint8)
        # Unpack using bitwise comparisons to 2**n
        bits = np.ones(1, np.uint8)
        for i in range(8):
            result[:, i::8] = np.bitwise_and(bits, data).astype(np.uint8)
            bits *= 2
        # Extra rows needed for packing odd dimensions
        spares = num_ints * 4 * 8 - self.dim1
        if spares:
            # noinspection PyTypeChecker
            array = np.where(result[:, :-spares] == 0, 0, 1)
        else:
            # noinspection PyTypeChecker
            array = np.where(result == 0, 0, 1)
        self.array = array.astype(np.int8).reshape((self.dim2, self.dim1))
