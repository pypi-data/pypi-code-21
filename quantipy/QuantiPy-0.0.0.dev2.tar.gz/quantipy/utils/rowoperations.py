# -*- coding: utf-8 -*-

import numpy as np

def unique_rows(a, return_index=False):
    """
    Get the unique rows of a numpy array. This solution is fast!
    To get the unique columns the numpy array must be transposed before and after this operation.

    :type a: np.ndarray
    :param a: A two-dimensional numpy array
    :type return_index: Bool
    :param return_index: If True, also returns the indices of array a that result in the unique array.
    """
    b = np.ascontiguousarray(a).view(np.dtype((np.void, a.dtype.itemsize * a.shape[1])))
    _, idx = np.unique(b, return_index=True)

    if return_index:
        return a[idx], idx
    else:
        return a[idx]

        

def find_rows(row, a):
    """
    Find all rows row in the array a. Returns the indices.

    :type a: np.ndarray
    :param a: A two-dimensional numpy array
    :type row: np.ndarray
    :param row: A one-dimensional numpy array. 
    """
    return np.where(np.all(row==a,axis=1))
    
