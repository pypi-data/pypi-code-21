#!/usr/bin/python
# -*- coding: utf-8 -*-

import numpy as np


def padArray(array, x, y, right=True, bottom=True):
    a = np.empty((x - array.shape[0], array.shape[1]), dtype=array.dtype)
    a.fill(-1)
    array = np.vstack((array, a) if right else (a, array))
    a = np.empty((array.shape[0], y - array.shape[1]), dtype=array.dtype)
    a.fill(-1)
    array = np.hstack((array, a) if bottom else (a, array))
    return array
