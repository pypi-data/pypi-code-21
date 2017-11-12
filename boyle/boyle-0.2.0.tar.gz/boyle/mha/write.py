# coding=utf-8
# -------------------------------------------------------------------------------
# Author: Alexandre Manhaes Savio <alexsavio@gmail.com>
#
# 2015, Alexandre Manhaes Savio
# Use this at your own risk!
# -------------------------------------------------------------------------------
"""
Helper functions to write image data to .mha files
"""
from collections import OrderedDict
from check import _shiftdim

# TODO: WRITE FILE FOLLOWING THE MHD_TAGS in tags.py
def to_file(filename, data, size, spacing, offset, dtype,
            direction_cosines, overwrite=False):
    """
    This method writes the object parameters to a mha file.

    Parameters
    ----------
    filename: str
        Path to the .mha file.

    size: list or iterable of ints
        3D/4D matrix size

    spacing: list or iterable of float
        voxel size

    offset: list or iterable of int
        spatial offset of data data

    dtype: str
        Choices: 'short', 'float' or 'uchar'

    direction_cosines: list or iterable of float
        direction cosines of the raw image/vf

    overwrite: bool
        If `filename` exists already `overwrite` is False, will
        raise an IOError exception. Otherwise, the file will
        be overwritten.
    """
    # Check if the file extension is ".mha"
    if not filename.endswith('.mha'):
        log.warn('The output file path extension is not .mha.')

    if op.exists(filename) and not overwrite:
        raise IOError('File {} already exists, not overwriting.'.format(input_file))

    # Order the matrix in the proper way
    data = np.array(data, order = "F")

    # Check if the input matrix is an image or a vf
    if data.ndim == 3:
        data_type = 'img'
    elif data.ndim == 4:
        data_type = 'vf'

    with open(filename, 'wb') as f:
        # Write mha header
        f.write('ObjectType = Image\n')
        f.write('NDims = 3\n')
        f.write('BinaryData = True\n')
        f.write('BinaryDataByteOrderMSB = False\n')
        f.write('CompressedData = False\n')
        f.write('TransformMatrix = '+str(direction_cosines).strip('()[]').replace(',','')+'\n')
        f.write('Offset = '+str(offset).strip('()[]').replace(',','')+'\n')
        f.write('CenterOfRotation = 0 0 0\n')
        f.write('AnatomicalOrientation = RAI\n')
        f.write('ElementSpacing = '+str(spacing).strip('()[]').replace(',','')+'\n')
        f.write('DimSize = '+str(size).strip('()[]').replace(',','')+'\n')
        if data == 'vf':
            f.write('ElementNumberOfChannels = 3\n')
            data = _shiftdim(data, 3) ## Shift dimensions if the input matrix is a vf

        if data_type == 'short':
            f.write('ElementType = MET_SHORT\n')
        elif data_type == 'float':
            f.write('ElementType = MET_FLOAT\n')
        elif data_type == 'uchar':
            f.write('ElementType = MET_UCHAR\n')
        f.write('ElementDataFile = LOCAL\n')

        # Write matrix
        f.write(data)
