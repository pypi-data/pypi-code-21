# Licensed under an MIT open source license - see LICENSE

# from unittest import TestCase

# import numpy as np
# import numpy.testing as npt
# import matplotlib.pyplot as p
# import numpy as np
# from astropy import units as u
# from fil_finder import fil_finder_2D

# from _testing_data import *


# class Pad_Test(TestCase):

#     def test_pad_size(self):

#         test1 = fil_finder_2D(img, header=hdr, beamwidth=10.0 * u.arcsec,
#                               flatten_thresh=95,
#                               distance=260 * u.pc, size_thresh=430,
#                               glob_thresh=20, save_name="test1",
#                               pad_size=6, skeleton_pad_size=5)

#         test1.create_mask(border_masking=False, regrid=True, test_mode=False)
#         test1.medskel()
#         test1.analyze_skeletons()

#         test2 = fil_finder_2D(img, header=hdr, beamwidth=10.0 * u.arcsec,
#                               flatten_thresh=95,
#                               distance=260 * u.pc, size_thresh=430,
#                               glob_thresh=20, save_name="test1",
#                               pad_size=5, skeleton_pad_size=5)

#         test2.create_mask(border_masking=False, regrid=True, test_mode=False)
#         test2.medskel()
#         test2.analyze_skeletons()

#         npt.assert_allclose(test1.skeleton_nopad, test2.skeleton_nopad)

#         for arr1, arr2 in zip(test1.filament_arrays['final'],
#                               test2.filament_arrays['final']):
#             assert np.allclose(arr1[1:-1], arr2)

#         for arr1, arr2 in zip(test1.filament_arrays['long path'],
#                               test2.filament_arrays['long path']):
#             assert np.allclose(arr1[1:-1], arr2)
