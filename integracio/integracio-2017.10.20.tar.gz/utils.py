#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ctypes
import numpy as np
from . import _cgracio_f, _cgracio_d


class IntegracioError(ValueError):
    pass


class PoniError(IntegracioError):
    pass


class PrecisionError(IntegracioError):
    pass


class _geometry_struct_f(ctypes.Structure):
    _fields_ = [
        ('distance', ctypes.c_float),
        ('poni1', ctypes.c_float),
        ('poni2', ctypes.c_float),
        ('pixelsize1', ctypes.c_float),
        ('pixelsize2', ctypes.c_float),
        ('rot1', ctypes.c_float),
        ('rot2', ctypes.c_float),
        ('rot3', ctypes.c_float),
        ('wavelength', ctypes.c_float),
        ('units', ctypes.c_int),
        ('radmin', ctypes.c_float),
        ('radmax', ctypes.c_float),
        ('pol', ctypes.c_float),
        ('sa', ctypes.c_int),
        ('bins', ctypes.c_int),
    ]


class _geometry_struct_d(ctypes.Structure):
    _fields_ = [
        ('distance', ctypes.c_double),
        ('poni1', ctypes.c_double),
        ('poni2', ctypes.c_double),
        ('pixelsize1', ctypes.c_double),
        ('pixelsize2', ctypes.c_double),
        ('rot1', ctypes.c_double),
        ('rot2', ctypes.c_double),
        ('rot3', ctypes.c_double),
        ('wavelength', ctypes.c_double),
        ('units', ctypes.c_int),
        ('radmin', ctypes.c_double),
        ('radmax', ctypes.c_double),
        ('pol', ctypes.c_double),
        ('sa', ctypes.c_int),
        ('bins', ctypes.c_int),
    ]


_geometry_structs = {
    'float': _geometry_struct_f,
    'double': _geometry_struct_d,
}

# noinspection PyUnresolvedReferences
_types = {
    'float': np.float32,
    'double': np.float64,
}


_modules = {
    'float': _cgracio_f,
    'double': _cgracio_d,
}


def geometry_by_precision(precision):
    try:
        return _geometry_structs[precision]
    except KeyError:
        raise PrecisionError(f'Precision {precision} is unknown. Possible values: {",".join(_geometry_structs.keys())}')


def type_by_precision(precision):
    try:
        return _types[precision]
    except KeyError:
        raise PrecisionError(f'Precision {precision} is unknown. Possible values: {",".join(_types.keys())}')


def integration(precision):
    try:
        return _modules[precision]._integration
    except KeyError:
        raise PrecisionError(f'Precision {precision} is unknown. Possible values: {",".join(_modules.keys())}')


def results(precision):
    try:
        return _modules[precision]._results
    except KeyError:
        raise PrecisionError(f'Precision {precision} is unknown. Possible values: {",".join(_modules.keys())}')
