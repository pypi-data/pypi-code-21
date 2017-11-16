"""
Data Access with Numpy
----------------------
"""
from __future__ import absolute_import

import numpy as np

from ctypes import (memmove, POINTER, sizeof, c_double, c_float, c_int32,
                    c_int16, c_int8)

def as_numpy_array(arr):
    _dtypes = {
        c_double: np.float64,
        c_float: np.float32,
        c_int32: np.int32,
        c_int16: np.int16,
        c_int8: np.int8}
    ctype = arr.c_type
    size = len(arr)
    data = np.empty((size,), dtype=_dtypes[ctype])
    data_ptr = data.ctypes.data_as(POINTER(ctype))
    data_size = sizeof(ctype)*size
    memmove(data_ptr, arr.copy(), data_size)
    return data
