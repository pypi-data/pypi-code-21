# -*- coding: utf-8 -*-
import numpy as np
import numpy.lib.arraypad as padlib


def pad_constant(array, pad_width, constant_values):
    if not issubclass(array.dtype.type, np.character):
        return np.pad(array, pad_width, "constant", constant_values=constant_values)
    narray = np.array(array)
    pad_width = padlib._validate_lengths(narray, pad_width)
    constant_values = padlib._normalize_shape(narray, constant_values, cast_to_int=False)
    newmat = narray.copy()
    for axis, ((pad_before, pad_after), (before_val, after_val)) \
            in enumerate(zip(pad_width, constant_values)):
        newmat = _prepend_const(newmat, pad_before, before_val, axis)
        newmat = _append_const(newmat, pad_after, after_val, axis)
    return newmat


def _prepend_const(arr, pad_amt, val, axis=-1):
    """
    Prepend constant `val` along `axis` of `arr`.

    Parameters
    ----------
    arr : ndarray
        Input array of arbitrary shape.
    pad_amt : int
        Amount of padding to prepend.
    val : scalar
        Constant value to use. For best results should be of type `arr.dtype`;
        if not `arr.dtype` will be cast to `arr.dtype`.
    axis : int
        Axis along which to pad `arr`.

    Returns
    -------
    padarr : ndarray
        Output array, with `pad_amt` constant `val` prepended along `axis`.

    """
    if pad_amt == 0:
        return arr
    padshape = tuple(x if i != axis else pad_amt
                     for (i, x) in enumerate(arr.shape))
    if val == 0:
        return np.concatenate((np.zeros(padshape, dtype=arr.dtype), arr),
                              axis=axis)
    else:
        mat = np.empty(padshape, type(val))
        mat.fill(val)
        return np.concatenate((mat, arr), axis=axis)


def _append_const(arr, pad_amt, val, axis=-1):
    """
    Append constant `val` along `axis` of `arr`.

    Parameters
    ----------
    arr : ndarray
        Input array of arbitrary shape.
    pad_amt : int
        Amount of padding to append.
    val : scalar
        Constant value to use. For best results should be of type `arr.dtype`;
        if not `arr.dtype` will be cast to `arr.dtype`.
    axis : int
        Axis along which to pad `arr`.

    Returns
    -------
    padarr : ndarray
        Output array, with `pad_amt` constant `val` appended along `axis`.

    """
    if pad_amt == 0:
        return arr
    padshape = tuple(x if i != axis else pad_amt
                     for (i, x) in enumerate(arr.shape))
    if val == 0:
        return np.concatenate((arr, np.zeros(padshape, dtype=arr.dtype)),
                              axis=axis)
    else:
        mat = np.empty(padshape, type(val))
        mat.fill(val)
        return np.concatenate((arr, mat), axis=axis)
