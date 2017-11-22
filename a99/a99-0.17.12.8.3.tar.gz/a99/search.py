"""
Search tools
"""

__all__ = [
"index_nearest", "BSearch", "BSearchRound", "BSearchCeil", "BSearchFloor", "FindNotNaNBackwards", ]



from bisect import *
import numpy as np



def index_nearest(array, value):
    """
    Finds index of nearest value in array.

    Args:
        array: numpy array
        value:

    Returns:
        int

    http://stackoverflow.com/questions/2566412/find-nearest-value-in-numpy-array
    """
    idx = (np.abs(array-value)).argmin()
    return idx



def BSearch(a, x, lo=0, hi=None):
    """Returns index of x in a, or -1 if x not in a.

    Arguments:
      a -- ordered numeric sequence
      x -- element to search within a
      lo -- lowest index to consider in search*
      hi -- highest index to consider in search*

    *bisect.bisect_left capability that we don't need to loose."""
    if len(a) == 0: return -1
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return pos if pos != hi and a[pos] == x else -1  # doesn't walk off the end


def BSearchRound(a, x, lo=0, hi=None):
    """Returns index of a that is closest to x.

    Arguments:
      a -- ordered numeric sequence
      x -- element to search within a
      lo -- lowest index to consider in search*
      hi -- highest index to consider in search*

    *bisect.bisect_left capability that we don't need to loose."""
    if len(a) == 0: return -1
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)

    if pos >= hi:
        return hi - 1
    elif a[pos] == x or pos == lo:
        return pos
    else:
        return pos - 1 if x - a[pos - 1] <= a[pos] - x else pos


def BSearchCeil(a, x, lo=0, hi=None):
    """Returns lowest i such as a[i] >= x, or -1 if x > all elements in a

    So, if x is in between two elements in a, this function will return the
    index of the higher element, hence "Ceil".

    Arguments:
      a -- ordered numeric sequence
      x -- element to search within a
      lo -- lowest index to consider in search
      hi -- highest index to consider in search"""
    if len(a) == 0: return -1
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return pos if pos < hi else -1


def BSearchFloor(a, x, lo=0, hi=None):
    """Returns highest i such as a[i] <= x, or -1 if x < all elements in a

    So, if x is in between two elements in a, this function will return the
    index of the lower element, hence "Floor".

    Arguments:
      a -- ordered numeric sequence
      x -- element to search within a
      lo -- lowest index to consider in search
      hi -- highest index to consider in search"""
    if len(a) == 0: return -1
    hi = hi if hi is not None else len(a)
    pos = bisect_left(a, x, lo, hi)
    return pos - 1 if pos >= hi \
        else (pos if x == a[pos] else (pos - 1 if pos > lo else -1))


def FindNotNaNBackwards(x, i):
    """Returns last position (starting at i backwards) which is not NaN, or -1."""
    while i >= 0:
        if not np.isnan(x[i]):
            return i
        i -= 1
    return -1
