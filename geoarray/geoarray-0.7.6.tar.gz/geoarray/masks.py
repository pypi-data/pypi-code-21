# -*- coding: utf-8 -*-

import numpy as np

# internal imports
from .baseclasses import GeoArray

__author__ = 'Daniel Scheffler'


class BadDataMask(GeoArray):
    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=False, progress=True,
                 q=False):
        super(BadDataMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                          bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        if self.is_inmem:
            # validate input data - before converting to bool
            self._validate_array_values(self.arr)
            self.arr = self.arr.astype(np.bool)

            # del self._mask_baddata, self.mask_baddata # TODO delete property (requires deleter)

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array!"
        self._validate_array_values(ndarray)
        self._arr = ndarray.astype(np.bool)

    def _validate_array_values(self, maskarray):
        pixelVals_in_mask = sorted(list(np.unique(maskarray)))
        assert len(pixelVals_in_mask) <= 2, 'Bad data mask must have only two pixel values (boolean) - 0 and 1 or ' \
                                            'False and True! The given mask for %s contains the values %s.' \
                                            % (self.basename, pixelVals_in_mask)
        assert pixelVals_in_mask in [[0, 1], [0], [1], [False, True], [False], [True]], \
            'Found unsupported pixel values in the given bad data mask for %s: %s. Only the values True, False, 0 ' \
            'and 1 are supported. ' % (self.basename, pixelVals_in_mask)


class NoDataMask(GeoArray):
    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=False, progress=True,
                 q=False):
        super(NoDataMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                         bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        if self.is_inmem:
            # validate input data - before converting to bool
            self._validate_array_values(self.arr)
            self.arr = self.arr.astype(np.bool)

            # del self._mask_nodata, self.mask_nodata # TODO delete property (requires deleter)
            # TODO disk-mode: init must check the numbers of bands, and ideally also the pixel values in mask

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array!"
        self._validate_array_values(ndarray)
        self._arr = ndarray.astype(np.bool)

    def _validate_array_values(self, maskarray):
        pixelVals_in_mask = sorted(list(np.unique(maskarray)))
        assert len(pixelVals_in_mask) <= 2, 'Nodata mask must have only two pixel values (boolean) - 0 and 1 or ' \
                                            'False and True! The given mask for %s contains the values %s.' % (
                                                self.basename, pixelVals_in_mask)
        assert pixelVals_in_mask in [[0, 1], [0], [1], [False, True], [False], [True]], \
            'Found unsupported pixel values in the given Nodata mask for %s: %s. Only the values True, False, 0 ' \
            'and 1 are supported. ' % (self.basename, pixelVals_in_mask)


class CloudMask(GeoArray):
    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=None, progress=True,
                 q=False):
        # TODO implement class definitions and specific metadata

        super(CloudMask, self).__init__(path_or_array, geotransform=geotransform, projection=projection,
                                        bandnames=bandnames, nodata=nodata, progress=progress, q=q)

        # del self._mask_nodata, self.mask_nodata # TODO delete property (requires deleter)
        # TODO check that: "Automatically detected nodata value for CloudMask 'IN_MEM': 1.0"

    def to_ENVI_classification(self):  # pragma: no cover
        raise NotImplementedError  # TODO
