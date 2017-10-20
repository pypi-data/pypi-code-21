#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Test Units
"""
#==============================================================================
# Import what is needed here:
import numpy as np

from .. import FaceDetector

import pkg_resources

import bob.io.base

def test_face_detector():
    """
    Test FaceDetector class.
    """

    image = np.zeros((3, 100, 100))

    result = FaceDetector().detect_single_face(image)

    assert result is None

    image = np.ones((3, 100, 100))

    result = FaceDetector().detect_single_face(image)

    assert result is None

    # test on the actual image:
    test_file = pkg_resources.resource_filename('bob.ip.dlib', 'data/test_image.hdf5')

    f = bob.io.base.HDF5File(test_file) #read only
    image = f.read('image') #reads integer
    del f

    result = FaceDetector().detect_single_face(image)

    assert result[0].topleft == (0, 236)

    assert result[0].bottomright == (84, 312)


