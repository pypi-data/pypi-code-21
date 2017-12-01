#!/usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import cryio


def correctImage(beamline, itype, array):
    if beamline == 'Dubble':
        if itype == 'saxs':
            array = np.rot90(array, 3)
        elif itype == 'waxs':
            array = np.rot90(array, 1)
    elif beamline == 'SNBL':
        array = np.rot90(array[::-1], 3)
    return array


def correctMask(beamline, itype, mask):
    if isinstance(mask, cryio.fit2dmask.Fit2DMask):
        if beamline == 'SNBL':
            mask.array = mask.array[::-1]
    elif isinstance(mask, cryio.numpymask.NumpyMask):
        if beamline == 'Dubble':
            if itype == 'saxs':
                mask.array = np.rot90(mask.array, 1)
            elif itype == 'waxs':
                mask.array = np.rot90(mask.array, 3)
        elif beamline == 'SNBL':
            mask.array = np.rot90(mask.array[::-1], 3)
    return mask
