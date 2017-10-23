#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Fork of fabio edf reader
"""

import mmap
import numpy as np
from . import cbfimage, templates, cryioimage


class EdfError(cryioimage.ImageError):
    pass


class EdfImage(cryioimage.CryioImage):
    Extensions = '.edf',
    EDF_HEADER_BEGIN = b'{'
    EDF_HEADER_END = b'}'
    DTYPE = {  # borrowed from fabio
        "SignedByte": np.int8,
        "Signed8": np.int8,
        "UnsignedByte": np.uint8,
        "Unsigned8": np.uint8,
        "SignedShort": np.int16,
        "Signed16": np.int16,
        "UnsignedShort": np.uint16,
        "Unsigned16": np.uint16,
        "UnsignedShortInteger": np.uint16,
        "SignedInteger": np.int32,
        "Signed32": np.int32,
        "UnsignedInteger": np.uint32,
        "Unsigned32": np.uint32,
        "SignedLong": np.int32,
        "UnsignedLong": np.uint32,
        "Signed64": np.int64,
        "Unsigned64": np.uint64,
        "FloatValue": np.float32,
        "FLOATVALUE": np.float32,
        "FLOAT": np.float32,  # fit2d
        "Float": np.float32,  # fit2d
        "FloatIEEE32": np.float32,
        "Float32": np.float32,
        "Double": np.float64,
        "DoubleValue": np.float64,
        "FloatIEEE64": np.float64,
        "DoubleIEEE64": np.float64
    }
    TYPE2STR = {
        np.dtype('int8'): "SignedByte",
        np.dtype('int16'): "SignedShort",
        np.dtype('int32'): "SignedInteger",
        np.dtype('int64'): "Signed64",
        np.dtype('uint8'): "UnsignedByte",
        np.dtype('uint16'): "UnsignedShort",
        np.dtype('uint32'): "UnsignedInteger",
        np.dtype('uint64'): "Unsigned64",
        np.dtype('float32'): "FloatValue",
        np.dtype('float64'): "DoubleValue",
        # np.dtype('float128'): "QuadrupleValue",  # it does not exist in win32 numpy
    }

    def __init__(self, filepath=None):
        super().__init__(filepath)
        self._offset = 0
        if self.filepath:
            self._read()

    def _read(self):
        with open(self.filepath, 'rb') as f:
            try:
                self._map = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
            except (mmap.error, IOError):
                self._map = f.read()
        self._seek_header()
        if self._begin == -1 or self._end == -1:
            raise EdfError('Could not find header tokens in {}. Might it be not an EDF?'.format(self.filepath))
        self._parse()
        self.multiframe = self._begin != -1 and self._end != -1

    def __iter__(self):
        while True:
            yield self
            if self._begin == -1 or self._end == -1:
                raise StopIteration
            self._parse()

    def _seek_header(self):
        self._begin = self._map.find(self.EDF_HEADER_BEGIN, self._offset) + 1
        self._end = self._map.find(self.EDF_HEADER_END, self._offset)

    def _parse(self):
        self._parse_header()
        self._parse_binary()
        self._seek_header()

    def _get_chunk(self, start, size):
        end = start + size
        self._offset = end
        return self._map[start:end]

    def _parse_header(self):
        raw = self._get_chunk(self._begin, self._end-self._begin).decode()
        self.header = {}
        for line in raw.splitlines():
            try:
                key, value = line.strip(' ;').split('=')
            except ValueError:
                continue
            value = value.strip().split(' ')
            key = key.strip()
            if not value:
                continue
            elif len(value) == 1:
                value = value[0]
                try:
                    self.header[key] = float(value) if '.' in value else int(value)
                except ValueError:
                    self.header[key] = value
            else:
                try:
                    self.header[key] = [float(i) if '.' in i else int(i) for i in value]
                except ValueError:
                    self.header[key] = value
        if not self.header:
            raise EdfError('Could not parse EDF header or it is empty in {}'.format(self.filepath))
        # Some files do not contains "Size" key, we have to get the type here to calculate size correctly
        self._parse_type()
        if 'Size' not in self.header:
            if 'Dim_1' in self.header and 'Dim_2' in self.header:
                self.header['Size'] = self.header['Dim_1'] * self.header['Dim_2'] * self.header['ntype'].itemsize
            else:
                raise EdfError('The EDF image header of {0} does not contain "Size" key.'.format(self.filepath))

    def _parse_type(self):
        try:
            t = self.DTYPE[self.header['DataType']]
        except KeyError:
            t = np.int32
        dt = np.dtype(t)
        if 'ByteOrder' in self.header and self.header['ByteOrder'] == 'HighByteFirst':
            dt.newbyteorder('>')
        self.header['ntype'] = dt

    def _parse_binary(self,):
        binsize = int(self.header['Size'])
        start = self._end + 2  # }\n
        raw = self._get_chunk(start, binsize)
        self.array = np.frombuffer(raw, self.header['ntype']).reshape((self.header['Dim_2'], self.header['Dim_1']))
        self.array.flags.writeable = True

    def save(self, filepath, fmt='cbf', **kwargs):
        try:
            {
                'cbf': self.save_cbf,
                'edf': self.save_edf,
            }[fmt](filepath, **kwargs)
        except KeyError:
            raise EdfError('Format is unknown')

    def save_cbf(self, filepath, **kwargs):
        cbf = cbfimage.CbfImage()
        cbf.array = self.array
        cbf.header.update(kwargs)
        cbf.save_cbf(filepath, **kwargs)

    def save_edf(self, filepath, **kwargs):
        if self.array is None:
            return
        shapeX, shapeY = self.array.shape
        binary_blob = self.array.reshape((shapeX, shapeY)).tostring()
        edf = self.header
        edf.update({
            'binsize': len(binary_blob),
            'headersize': 2560,
            'dim_1': shapeY,
            'dim_2': shapeX,
            'datatype': self.TYPE2STR[self.array.dtype]
        })
        edf.update(kwargs)
        header = templates.get_template('edf_header').render(edf)
        header = '{}\n'.format(header[:-2]).encode('ascii', errors='ignore')
        with open(filepath, 'wb') as fedf:
            fedf.write(header)
            fedf.write(binary_blob)
