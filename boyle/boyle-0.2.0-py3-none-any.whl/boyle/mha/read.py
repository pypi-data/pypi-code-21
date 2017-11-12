# coding=utf-8
# -------------------------------------------------------------------------------
# Author: Alexandre Manhaes Savio <alexsavio@gmail.com>
#
# 2015, Alexandre Manhaes Savio
# Use this at your own risk!
# -------------------------------------------------------------------------------
"""
Helper functions to read .mha files
"""
import logging

import numpy as np

from check import _check_dtype, _check_mha_file, _cast2int, _shiftdim
from tags import MHD_TAGS

logging.basicConfig(level=logging.DEBUG)

log = logging.getLogger(__file__)


def load_from_file(filename):
    """
    This method reads a mha file.

    Parameters
    ----------
    filename: str
        Path to the .mha file.
    """
    try:
        _check_mha_file(filename)
        data, hdr = _read_img(filename)
    except Exception as ex:
        raise Exception('Error loading file {}.'.format(filename)) from ex
    else:
        return data, hdr


def _read_img(filename):
    """ Read the file in `filename`.

    Parameters
    ----------
    filename: str
        Path to the .mha file.

    Returns
    -------
    data: np.array
        3D or 4D array with the image data.

    hdr: dict
        dictionary with metadata of the file.
    """
    data = None
    hdr  = {}

    log.debug('Reading header from image {}.'.format(filename))

    with open(filename, 'rb') as f:
        # On default the matrix is considered to be an image
        data_type = 'img'

        # Read mha header
        for r in range(len(MHD_TAGS)):
            row = f.readline()
            log.debug('Processing "{}"'.format(row))

            field_and_value = row.split(b'=')
            field_name      = field_and_value[0].strip().decode()
            field_value     = field_and_value[1].strip().decode()

            log.debug('{} - {}'.format(field_name, field_value))

            if field_name == 'TransformMatrix':
                hdr[field_name] = _cast2int([float(v) for v in field_value.split()])

            elif field_name == 'Offset':
                hdr[field_name] = _cast2int([float(v) for v in field_value.split()])

            elif field_name == 'ElementSpacing':
                hdr[field_name] = _cast2int([float(v) for v in field_value.split()])

            elif field_name == 'DimSize':
                hdr[field_name] = [int(v) for v in field_value.split()]

            elif field_name == 'ElementType':
                hdr[field_name] = field_value

            elif field_name == 'ElementNumberOfChannels':
                if row.startswith(b'ElementNumberOfChannels = 3'):
                    data_type = 'vf'  # The matrix is a vf
                    hdr[field_name] = _cast2int([int(v) for v in field_value.split()])

            elif field_name == 'ElementDataFile':
                data = b''.join(f.readlines())
                break

            # other fields from MHD_TAGS
            else:
                if field_name in MHD_TAGS:
                    hdr[field_name] = field_value
                else:
                    raise ValueError('Found unknown tag {} in '
                                     'file {}.'.format(field_name,
                                                       filename))

        # check if it read data
        if data is None:
            raise IOError('Could not read `ElementDataFile` from '
                          'the file {}.'.format(filename))

        # Read raw data
        dtype = hdr['ElementType']
        size  = hdr['DimSize']
        numpy_type, mhd_type = _check_dtype(dtype)

        # Raw data from string to array
        data = np.fromstring(data, dtype=numpy_type)

        # Reshape array
        if data_type == 'img':
            data = data.reshape(size[2],
                                size[1],
                                size[0]
                                ).T
        elif data_type == 'vf':
            data = data.reshape(size[2],
                                size[1],
                                size[0],
                                3
                                )
            data = _shiftdim(data, 3).T

        return data, hdr
