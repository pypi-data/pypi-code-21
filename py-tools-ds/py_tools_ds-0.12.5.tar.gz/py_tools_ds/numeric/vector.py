# -*- coding: utf-8 -*-

import collections
import numpy as np
import bisect

__author__ = "Daniel Scheffler"


def find_nearest(array, value, roundAlg='auto', extrapolate=False, exclude_val=False):
    """finds the value of an array nearest to a another single value
    NOTE: In case of extrapolation an EQUALLY INCREMENTED array (like a coordinate grid) is assumed!

    :param array:
    :param value:
    :param roundAlg:    <str> 'auto', 'on', 'off'
    :param extrapolate: extrapolate the given array if the given value is outside the array
    :param exclude_val:
    """
    assert roundAlg in ['auto', 'on', 'off']
    assert isinstance(array, list) or (isinstance(array, np.ndarray) and len(array.shape) == 1)
    array = sorted(list(array))

    if exclude_val and value in array:
        array.remove(value)

    if extrapolate:
        increment = abs(array[1] - array[0])
        if value > max(array):  # expand array until value
            array = np.arange(min(array), value + increment, increment)
        if value < min(array):  # negatively expand array until value
            array = (np.arange(max(array), value - increment, -increment))[::-1]
    elif value < min(array) or value > max(array):
        raise ValueError('Value %s is outside of the given array.' % value)

    if roundAlg == 'auto':
        diffs = np.abs(np.array(array) - value)
        minDiff = diffs.min()
        minIdx = diffs.argmin()
        isMiddleVal = collections.Counter(diffs)[minDiff] > 1
        out = array[minIdx] if not isMiddleVal else array[bisect.bisect_left(array, value)]
    elif roundAlg == 'off':
        idx = bisect.bisect_left(array, value)
        if array[idx] == value:
            out = value  # exact hit
        else:
            out = array[idx - 1]  # round off
    else:  # roundAlg == 'on'
        out = array[bisect.bisect_left(array, value)]

    return out
