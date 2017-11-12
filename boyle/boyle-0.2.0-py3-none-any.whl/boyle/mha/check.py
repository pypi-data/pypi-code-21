# coding=utf-8
# -------------------------------------------------------------------------------
# Author: Alexandre Manhaes Savio <alexsavio@gmail.com>
#
# 2015, Alexandre Manhaes Savio
# Use this at your own risk!
# -------------------------------------------------------------------------------

import logging
import os.path as op

import numpy as np
import six

from tags import MHD_TO_NUMPY_TYPE, NUMPY_TO_MHD_TYPE

log = logging.getLogger(__file__)


def _cast2int(l):
    l_new = []
    for i in l:
        if i.is_integer():
            l_new.append(int(i))
        else:
            l_new.append(i)
    return l_new


def _shiftdim(x, n):
    return x.transpose(np.roll(range(x.ndim), -n))


def _check_dtype(dtype):
    """ Raise an exception if `type` is not a valid input.

    Parameters
    ----------
    dtype: numpy.dtype or str
        Describes the `ElementType` of the matrix elements.
        You can either give a .mhd type descripton, e.g.,'MET_SHORT'
        or you can give a numpy.dtype, e.g., np.int8.
        See MHD_TO_NUMPY_TYPE for the available options.

    Returns
    -------
    numpy_dtype: type
        The type descriptor in numpy format

    mhd_type: str
        The type descriptor in MHD format
    """
    numpy_type = None
    mhd_type   = None
    # check if `dtype` is a MHD type string
    if isinstance(dtype, six.string_types):
        if dtype not in MHD_TO_NUMPY_TYPE:
            raise ValueError('Expected a string for `dtype`. Choices '
                             '({}), got {}.'.format(
                                        list(MHD_TO_NUMPY_TYPE.keys())),
                                        dtype,
                            )
        numpy_type = MHD_TO_NUMPY_TYPE[dtype]
        mhd_type   = dtype
    # check if `dtype` is a numpy type
    elif isinstance(dtype, type):
        if dtype not in NUMPY_TO_MHD_TYPE:
            raise ValueError('Expected a numpy type for `dtype`. Choices '
                             '({}), got {}.'.format(
                                        list(NUMPY_TO_MHD_TYPE.keys())),
                                        dtype,
                            )
        numpy_type = dtype
        mhd_type   = NUMPY_TO_MHD_TYPE[dtype]

    # check if the outputs have been assigned any value
    if numpy_type is None and mhd_type is None:
        raise ValueError('Could not find valid options for `dtype`.'
                         'Choices are in ({}), got {}.'.format(
                                        list(MHD_TO_NUMPY_TYPE.keys())),
                                        dtype,
                         )

    return numpy_type, mhd_type


def _check_mha_file(filename):
        """ Create a MHA object from a .mha file.

        Parameters
        ----------
        filename: str
            Path to the .mha file.

        Returns
        -------
        mha: MHA
            The MHA object instance.

        Raises
        ------
        IOError:
            If the file cannot be found.
        """
        if not op.exists(filename):
            raise IOError('Could not find file {}.'.format(filename))

        # Check if the file extension is ".mha"
        if not filename.endswith('.mha'):
            log.warn('File {} extension is not .mha.'.format(filename))
