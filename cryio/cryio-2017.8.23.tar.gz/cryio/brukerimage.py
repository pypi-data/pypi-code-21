#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fork of fabio bruker reader
"""

import os
import mmap
import numpy as np
from .cryioimage import CryioImage, ImageError


class BrukerError(ImageError):
    pass


class BrukerImage(CryioImage):
    Extensions = '.gfrm',
    line = 80
    blocksize = 512
    nhdrblks = 5  # by default we always read 5 blocks of 512
    version = 86
    size = {
        1: np.uint8,
        2: np.uint16,
        4: np.uint32,
    }

    def __init__(self, filepath=None):
        super().__init__(filepath)
        if self.filepath:
            self._read()

    def _read(self):
        with open(self.filepath, 'rb') as f:
            try:
                self._map = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            except (mmap.error, IOError):
                self._map = f
            try:
                self._readheader()
                npixelb = int(self.header['NPIXELB'])
            except (KeyError, ValueError, IndexError):
                raise BrukerImage(f'Bruker file {self.filepath} cannot be read')
            data = np.fromstring(self._map.read(self.dim1 * self.dim2 * npixelb), dtype=self.size[npixelb])
            if not np.little_endian and data.dtype.itemsize > 1:
                data.byteswap(True)

            data = data.astype(np.uint32)
            # handle overflows
            nov = int(self.header['NOVERFL'])
            while nov > 0:  # Read in the overflows
                nov -= 1
                # need at least int32 sized data I guess - can reach 2^21
                # 16 character overflows:
                #      9 characters of intensity
                #      7 character position
                intensity = self._map.read(9)
                position = self._map.read(7)
                data[int(position)] = int(intensity)
            # Handle Float images ...
            if 'LINEAR' in self.header:
                try:
                    slope, offset = map(float, self.header['LINEAR'].split(None, 1))
                    if slope != 1 or offset != 0:
                        data = (data * slope + offset).astype(np.float32)
                except (ValueError, KeyError, IndexError):
                    pass
            self.array = data.reshape(self.dim1, self.dim2)
            self._map = None

    def _readheader(self):
        """
        The bruker format uses 80 char lines in key : value format
        In the first 512*5 bytes of the header there should be a
        HDRBLKS key, whose value denotes how many 512 byte blocks
        are in the total header. The header is always n*5*512 bytes,
        otherwise it wont contain whole key: value pairs
        """
        headerbytes = self._map.read(self.blocksize * self.nhdrblks)
        for i in range(0, self.nhdrblks * self.blocksize, self.line):
            self._fillheader(headerbytes, i)
        # we must have read this in the first 5*512 bytes.
        nhdrblks = int(self.header.get('HDRBLKS', self.nhdrblks))
        self.header['HDRBLKS'] = nhdrblks
        # Now read in the rest of the header blocks, appending
        headerbytes += self._map.read(self.blocksize * (nhdrblks - self.nhdrblks))
        for i in range(self.nhdrblks * self.blocksize, nhdrblks * self.blocksize, self.line):
            self._fillheader(headerbytes, i)
        # make a (new) header item called "datastart"
        self.header['datastart'] = self.blocksize * nhdrblks
        # set the image dimensions
        self.dim1 = int(self.header['NROWS'].split()[0])
        self.dim2 = int(self.header['NCOLS'].split()[0])
        self.version = int(self.header.get('VERSION', self.version))

    def _fillheader(self, headerbytes, i):
        sls = headerbytes[i:i + self.line]
        if b':' in sls:
            key, val = [n.strip().decode('ascii') for n in sls.split(b':', 1)]
            if key in self.header:
                self.header[key] = f'{self.header[key]}{os.linesep}{val}'
            else:
                self.header[key] = val
