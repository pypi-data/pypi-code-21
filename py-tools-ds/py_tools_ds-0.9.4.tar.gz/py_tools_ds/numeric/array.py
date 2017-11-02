# -*- coding: utf-8 -*-
__author__ = "Daniel Scheffler"

import numpy as np


def get_outFillZeroSaturated(dtype):
    """Returns the values for 'fill-', 'zero-' and 'saturated' pixels of an image
    to be written with regard to the target data type.

    :param dtype: data type of the image to be written
    """
    dtype = str(np.dtype(dtype))
    assert dtype in ['int8', 'uint8', 'int16', 'uint16', 'float32'], \
        "get_outFillZeroSaturated: Unknown dType: '%s'." % dtype
    dict_outFill = {'int8': -128, 'uint8': 0, 'int16': -9999, 'uint16': 9999, 'float32': -9999.}
    dict_outZero = {'int8': 0, 'uint8': 1, 'int16': 0, 'uint16': 1, 'float32': 0.}
    dict_outSaturated = {'int8': 127, 'uint8': 256, 'int16': 32767, 'uint16': 65535, 'float32': 65535.}
    return dict_outFill[dtype], dict_outZero[dtype], dict_outSaturated[dtype]
