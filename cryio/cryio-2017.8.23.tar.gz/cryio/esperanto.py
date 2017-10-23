#!/usr/bin/python
# -*- coding: utf-8 -*-


import math
from datetime import datetime
import numpy as np
from . import _cryio, ImageError, tools, templates, cryioimage


class EsperantoException(ImageError):
    pass


class EsperantoImage(cryioimage.CryioImage):
    ESPERANTO_SIZE = 254  # -len('\r\n')

    def __init__(self, filepath=None):
        super().__init__(filepath)
        if self.filepath:
            self.parse()

    def parse(self):
        self.parse_header()
        self.parse_binary()

    def parse_header(self):
        raise NotImplementedError

    def parse_binary(self):
        raise NotImplementedError

    def save(self, filepath, array=None, pack=True, **kwargs):
        if array is None and self.array is None:
            raise EsperantoException('Nothing to save, an array is not provided')
        if array is None:
            array = self.array
        # crysalis reads only squared esperanto arrays with the x,x size divided by 4
        if array.shape[0] != array.shape[1] or array.shape[0] % 4 and array.shape[1] % 4:
            x = y = int(math.ceil(max(array.shape) / 4.0) * 4)
            array = tools.padArray(array, x, y)
        shape = array.shape[0]
        if pack:
            datatype = 'AGI_BITFIELD'
            espstr = bytes(_cryio._esp_encode(array.astype(np.int32)))
        else:
            datatype = '4BYTE_LONG'
            espstr = array.reshape((shape ** 2,)).astype(np.int32).tobytes()
        esp_header = {
            'shape': shape,
            'datetime': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f'),
            'datatype': datatype,
        }
        esp_header.update(kwargs)
        header = templates.get_template('esp_header').render(esp_header).splitlines()
        binblob = [bytes(l.ljust(self.ESPERANTO_SIZE).encode('ascii')) for l in header]
        with open(filepath, 'wb') as fedf:
            fedf.write(b'\r\n'.join(binblob))
            fedf.write(b'\r\n')
            fedf.write(espstr)
