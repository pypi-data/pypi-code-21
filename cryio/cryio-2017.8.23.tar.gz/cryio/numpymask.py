#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np
from .cryioimage import ImageError, CryioImage


class NotNumpyMask(ImageError):
    pass


class NumpyMask(CryioImage):
    Extensions = '.npz',

    def __init__(self, filepath=None):
        super().__init__(filepath)
        if self.filepath:
            self._read()

    def _read(self):
        try:
            self.array = np.load(self.filepath)['arr_0']
        except TypeError:
            raise NotNumpyMask(f'File "{self.filepath}" does not contain a numpy mask array')
