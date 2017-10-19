# coding: utf-8

# public items
__all__ = [
    'array',
    'ones',
    'zeros',
    'full',
    'empty',
    'ones_like',
    'zeros_like',
    'full_like',
    'empty_like',
]

# standard library
from uuid import uuid4

# dependent packages
import decode as dc
import numpy as np
import xarray as xr
from astropy import units as u
from astropy.io import fits


# functions
def array(data, tcoords=None, chcoords=None, scalarcoords=None, attrs=None, name=None):
    """Create an array as an instance of xarray.DataArray with Decode accessor.

    Args:
        data (numpy.ndarray): 2D (time x channel) array.
        tcoords (dict, optional): Dictionary of arrays that label time axis.
        chcoords (dict, optional): Dictionary of arrays that label channel axis.
        scalarcoords (dict, optional): Dictionary of values that don't label any axes (point-like).
        attrs (dict, optional): Dictionary of attributes to add to the instance.
        name (str, optional): String that names the instance.

    Returns:
        array (xarray.DataArray): Array.

    """
    # initialize coords with default values
    array = xr.DataArray(data, dims=('t', 'ch'), attrs=attrs, name=name)
    array.dca._initcoords()

    # update coords with input values (if any)
    if tcoords is not None:
        array.coords.update({key: ('t', tcoords[key]) for key in tcoords})

    if chcoords is not None:
        array.coords.update({key: ('ch', chcoords[key]) for key in chcoords})

    if scalarcoords is not None:
        array.coords.update(scalarcoords)

    return array


def zeros(shape, dtype=None, **kwargs):
    """Create an array of given shape and type, filled with zeros.

    Args:
        shape (sequence of ints): 2D shape of the array.
        dtype (data-type, optional): Desired data-type for the array.
        kwargs (optional): Other arguments of the array (*coords, attrs, and name).

    Returns:
        array (xarray.DataArray): Array filled with zeros.

    """
    data = np.zeros(shape, dtype)
    return dc.array(data, **kwargs)


def ones(shape, dtype=None, **kwargs):
    """Create an array of given shape and type, filled with ones.

    Args:
        shape (sequence of ints): 2D shape of the array.
        dtype (data-type, optional): Desired data-type for the array.
        kwargs (optional): Other arguments of the array (*coords, attrs, and name).

    Returns:
        array (xarray.DataArray): Array filled with ones.

    """
    data = np.ones(shape, dtype)
    return dc.array(data, **kwargs)


def full(shape, fill_value, dtype=None, **kwargs):
    """Create an array of given shape and type, filled with `fill_value`.

    Args:
        shape (sequence of ints): 2D shape of the array.
        fill_value (scalar or numpy.ndarray): Fill value or array.
        dtype (data-type, optional): Desired data-type for the array.
        kwargs (optional): Other arguments of the array (*coords, attrs, and name).

    Returns:
        array (xarray.DataArray): Array filled with `fill_value`.

    """
    return (dc.zeros(shape, **kwargs) + fill_value).astype(dtype)


def empty(shape, dtype=None, **kwargs):
    """Create an array of given shape and type, without initializing entries.

    Args:
        shape (sequence of ints): 2D shape of the array.
        dtype (data-type, optional): Desired data-type for the array.
        kwargs (optional): Other arguments of the array (*coords, attrs, and name).

    Returns:
        array (xarray.DataArray): Array without initializing entries.

    """
    data = np.empty(shape, dtype)
    return dc.array(data, **kwargs)


def zeros_like(array, dtype=None, keepmeta=True):
    """Create an array of zeros with the same shape and type as the input array.

    Args:
        array (xarray.DataArray): The shape and data-type of it define
            these same attributes of the output array.
        dtype (data-type, optional): If specified, this function overrides
            the data-type of the output array.
        keepmeta (bool, optional): Whether *coords, attrs, and name of the input
            array are kept in the output one. Default is True.

    Returns:
        array (xarray.DataArray): Array filled with zeros.

    """
    if keepmeta:
        return xr.zeros_like(array, dtype)
    else:
        return dc.zeros(array.shape, dtype)


def ones_like(array, dtype=None, keepmeta=True):
    """Create an array of ones with the same shape and type as the input array.

    Args:
        array (xarray.DataArray): The shape and data-type of it define
            these same attributes of the output array.
        dtype (data-type, optional): If spacified, this function overrides
            the data-type of the output array.
        keepmeta (bool, optional): Whether *coords, attrs, and name of the input
            array are kept in the output one. Default is True.

    Returns:
        array (xarray.DataArray): Array filled with ones.

    """
    if keepmeta:
        return xr.ones_like(array, dtype)
    else:
        return dc.ones(array.shape, dtype)


def full_like(array, fill_value, reverse=False, dtype=None, keepmeta=True):
    """Create an array of `fill_value` with the same shape and type as the input array.

    Args:
        array (xarray.DataArray): The shape and data-type of it define
            these same attributes of the output array.
        fill_value (scalar or numpy.ndarray): Fill value or array.
        dtype (data-type, optional): If spacified, this function overrides
            the data-type of the output array.
        keepmeta (bool, optional): Whether *coords, attrs, and name of the input
            array are kept in the output one. Default is True.

    Returns:
        array (xarray.DataArray): Array filled with `fill_value`.

    """
    if keepmeta:
        return (dc.zeros_like(array) + fill_value).astype(dtype)
    else:
        return dc.full(array.shape, fill_value, dtype)


def empty_like(array, dtype=None, keepmeta=True):
    """Create an array of empty with the same shape and type as the input array.

    Args:
        array (xarray.DataArray): The shape and data-type of it define
            these same attributes of the output array.
        dtype (data-type, optional): If spacified, this function overrides
            the data-type of the output array.
        keepmeta (bool, optional): Whether *coords, attrs, and name of the input
            array are kept in the output one. Default is True.

    Returns:
        array (xarray.DataArray): Array without initializing entries.

    """
    if keepmeta:
        return dc.empty(array.shape, dtype,
            tcoords=array.dca.tcoords, chcoords=array.dca.chcoords,
            scalarcoords=array.dca.scalarcoords, attrs=array.attrs, name=array.name
        )
    else:
        return dc.empty(array.shape, dtype)
