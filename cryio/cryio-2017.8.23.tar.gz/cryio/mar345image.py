#!/usr/bin/env python
# -*- coding: utf-8 -*-

import mmap
import ctypes
import struct
import numpy as np
from . import _cryio, cryioimage

MAR_MODE_DOSE = 0
MAR_MODE_TIME = 1
MAR_FORMAT_COMPRESSED = 1
MAR_FORMAT_SPIRAL = 2
MAR_MAGIC_NUMBER = 1234
MAR_BIN_HEADER_SIZE = 64
MAR_HEADER_SIZE = 4096
MAR_MAGIC_STRING1 = 'CCP4 packed image, X: {:04d}, Y: {:04d}\n'


class Mar345Error(cryioimage.ImageError):
    pass


class _LittleEndianBinaryHeader(ctypes.Structure):
    _format_ = '<16i'
    _fields_ = [
        ('magic_number', ctypes.c_int),
        ('dim1', ctypes.c_int),
        ('n_overflow', ctypes.c_int),
        ('format', ctypes.c_int),
        ('mode', ctypes.c_int),
        ('n_pixels', ctypes.c_int),
        ('pixel_length', ctypes.c_int),
        ('pixel_height', ctypes.c_int),
        ('wavelength', ctypes.c_int),
        ('distance', ctypes.c_int),
        ('start_phi', ctypes.c_int),
        ('end_phi', ctypes.c_int),
        ('start_omega', ctypes.c_int),
        ('end_omega', ctypes.c_int),
        ('chi', ctypes.c_int),
        ('two_theta', ctypes.c_int),
    ]

    def __init__(self, header):
        super(_LittleEndianBinaryHeader, self).__init__(*struct.unpack(self._format_, header))


class _BigEndianBinaryHeader(_LittleEndianBinaryHeader):
    _format_ = '>16i'


class Mar345Image(cryioimage.CryioImage):
    Extensions = '.mar3450', 'mar2300'

    def __init__(self, filepath=None):
        super().__init__(filepath)
        if self.filepath:
            self._read_mmap()
            self._parse_header()
            self._parse_binary()
            self._close_mmap()

    def _parse_header(self):
        self._parse_binary_header()
        self._parse_ascii_header()

    def _parse_binary(self):
        dim1 = self.binary_header.dim1
        dim2 = self.binary_header.n_pixels // dim1
        of = self.binary_header.n_overflow
        if self.binary_header.format == MAR_FORMAT_COMPRESSED:
            fs = MAR_MAGIC_STRING1.format(dim1, dim2).encode()
            s = self._mmap.find(fs)
            if s == -1:
                raise Mar345Error('Only mar v1 can be unpacked, v2 is not yet supported')
            ds = s + len(fs)  # data starts at
            self.array = np.asarray(_cryio._mar_decode(dim1, dim2, of, self._mmap[MAR_HEADER_SIZE:s], self._mmap[ds:]))
        elif self.binary_header.format == MAR_FORMAT_SPIRAL:
            raise Mar345Error('Cannot decode spiral mar format')
        else:
            raise Mar345Error('Mar format is unknown')

    def _parse_binary_header(self):
        self.binary_header = _LittleEndianBinaryHeader(self._mmap[:MAR_BIN_HEADER_SIZE])
        if self.binary_header.magic_number != MAR_MAGIC_NUMBER:
            self.binary_header = _BigEndianBinaryHeader(self._mmap[:MAR_BIN_HEADER_SIZE])

    def _parse_ascii_header(self):
        # ASCII header is absolutely useless, we do not waste time to parse it
        self.header = {}

    def _read_mmap(self):
        with open(self.filepath, 'rb') as f:
            try:
                self._mmap = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            except (mmap.error, IOError):
                self._mmap = f.read()

    def _close_mmap(self):
        if isinstance(self._mmap, mmap.mmap):
            self._mmap.close()
