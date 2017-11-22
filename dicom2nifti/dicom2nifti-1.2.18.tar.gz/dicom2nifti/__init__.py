# -*- coding: utf-8 -*-
"""
dicom2nifti

@author: abrys
"""

# noinspection PyUnresolvedReferences
from dicom2nifti.settings import disable_validate_sliceincrement, \
    disable_validate_orientation, \
    disable_validate_orthogonal, \
    disable_validate_slicecount, \
    disable_validate_multiframe_implicit, \
    enable_validate_orientation, \
    enable_validate_orthogonal, \
    enable_validate_slicecount, \
    enable_validate_sliceincrement, \
    enable_validate_multiframe_implicit
# noinspection PyUnresolvedReferences
from dicom2nifti.convert_dicom import dicom_series_to_nifti
# noinspection PyUnresolvedReferences
from dicom2nifti.convert_dir import convert_directory

# Setup the logger correctly
import logging
import sys

logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.WARNING)
