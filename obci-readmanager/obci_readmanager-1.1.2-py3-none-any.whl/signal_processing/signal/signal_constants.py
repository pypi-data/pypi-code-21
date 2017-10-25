# -*- coding: utf-8 -*-
# Copyright (c) 2016-2018 Braintech Sp. z o.o. [Ltd.] <http://www.braintech.pl>
# All rights reserved.

"""
Module providing constants for data proxy.

Author:
     Mateusz Kruszyński <mateusz.kruszynski@gmail.com>
"""
import numpy

SAMPLE_SIZES = {'DOUBLE': 8, 'FLOAT': 4}
SAMPLE_STRUCT_TYPES = {'DOUBLE': 'd', 'FLOAT': 'f'}
SAMPLE_NUMPY_TYPES = {'DOUBLE': numpy.float64, 'FLOAT': numpy.float32}


def sample_type_from_numpy(dtype):
    """Return DataWriteProxy compatible data type string from numpy dtype."""
    sample_type_numpy_d = dict((v, k) for k, v in SAMPLE_NUMPY_TYPES.items())
    for k in sample_type_numpy_d.keys():
        if dtype == k:
            return sample_type_numpy_d[k]
    raise KeyError("Unknown numpy type")
