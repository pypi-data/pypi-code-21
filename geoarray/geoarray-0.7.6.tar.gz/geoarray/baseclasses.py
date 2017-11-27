# -*- coding: utf-8 -*-

import os
import warnings
from importlib import util
from collections import OrderedDict

import numpy as np
from matplotlib import pyplot as plt
from osgeo import gdal_array
# custom
from shapely.geometry import Polygon
from shapely.wkt import loads as shply_loads
from six import PY3

# mpl_toolkits.basemap -> imported when GeoArray.show_map() is used
# dill -> imported when dumping GeoArray

try:
    from osgeo import gdal
    from osgeo import gdalnumeric
except ImportError:
    import gdal
    import gdalnumeric
from geopandas import GeoDataFrame, GeoSeries
from pandas import DataFrame
from py_tools_ds.convenience.object_oriented import alias_property
from py_tools_ds.geo.coord_calc import get_corner_coordinates
from py_tools_ds.geo.coord_grid import snap_bounds_to_pixGrid
from py_tools_ds.geo.coord_trafo import mapXY2imXY, imXY2mapXY, transform_any_prj, reproject_shapelyGeometry
from py_tools_ds.geo.projection import prj_equal, WKT2EPSG, EPSG2WKT, isLocal
from py_tools_ds.geo.raster.conversion import raster2polygon
from py_tools_ds.geo.vector.topology \
    import get_footprint_polygon, polyVertices_outside_poly, fill_holes_within_poly
from py_tools_ds.geo.vector.geometry import boxObj
from py_tools_ds.io.raster.gdal import get_GDAL_ds_inmem
from py_tools_ds.compatibility.gdal import get_gdal_func
from py_tools_ds.numeric.numbers import is_number
from py_tools_ds.numeric.array import get_array_tilebounds

#  internal imports
from .subsetting import get_array_at_mapPos

if PY3:
    # noinspection PyCompatibility
    from builtins import TimeoutError, FileNotFoundError
else:
    from py_tools_ds.compatibility.python.exceptions import TimeoutError, FileNotFoundError

__author__ = 'Daniel Scheffler'


class GeoArray(object):
    def __init__(self, path_or_array, geotransform=None, projection=None, bandnames=None, nodata=None, progress=True,
                 q=False):
        # type: (any, tuple, str, list, float, bool, bool) -> None
        """This class creates a fast Python interface for geodata - either on disk or in memory. It can be instanced with
        a file path or with a numpy array and the corresponding geoinformation. Instances can always be indexed like
        normal numpy arrays, no matter if GeoArray has been instanced from file or from an in-memory array. GeoArray
        provides a wide range of geo-related attributes belonging to the dataset as well as some functions for quickly
        visualizing the data as a map, a simple image or an interactive image.

        :param path_or_array:   a numpy.ndarray or a valid file path
        :param geotransform:    GDAL geotransform of the given array or file on disk
        :param projection:      projection of the given array or file on disk as WKT string
                                (only needed if GeoArray is instanced with an array)
        :param bandnames:       names of the bands within the input array, e.g. ['mask_1bit', 'mask_clouds'],
                                (default: ['B1', 'B2', 'B3', ...])
        :param nodata:          nodata value
        :param progress:        show progress bars (default: True)
        :param q:               quiet mode (default: False)
        """

        # TODO implement compatibility to GDAL VRTs
        if not (isinstance(path_or_array, (str, np.ndarray, GeoArray)) or
           issubclass(getattr(path_or_array, '__class__'), GeoArray)):
            raise ValueError("%s parameter 'arg' takes only string, np.ndarray or GeoArray(and subclass) instances. "
                             "Got %s." % (self.__class__.__name__, type(path_or_array)))

        if path_or_array is None:
            raise ValueError("The %s parameter 'path_or_array' must not be None!" % self.__class__.__name__)

        if isinstance(path_or_array, str):
            assert ' ' not in path_or_array, "The given path contains whitespaces. This is not supported by GDAL."

            if not os.path.exists(path_or_array):
                raise FileNotFoundError(path_or_array)

        if isinstance(path_or_array, GeoArray) or issubclass(getattr(path_or_array, '__class__'), GeoArray):
            self.__dict__ = path_or_array.__dict__.copy()
            self._initParams = dict([x for x in locals().items() if x[0] != "self"])
            self.geotransform = geotransform or self.geotransform
            self.projection = projection or self.projection
            self.bandnames = bandnames or list(self.bandnames.values())
            self._nodata = nodata if nodata is not None else self._nodata
            self.progress = False if progress is False else self.progress
            self.q = q if q is not None else self.q

        else:
            self._initParams = dict([x for x in locals().items() if x[0] != "self"])
            self.arg = path_or_array
            self._arr = path_or_array if isinstance(path_or_array, np.ndarray) else None
            self.filePath = path_or_array if isinstance(path_or_array, str) and path_or_array else None
            self.basename = os.path.splitext(os.path.basename(self.filePath))[0] if not self.is_inmem else 'IN_MEM'
            self.progress = progress
            self.q = q
            self._arr_cache = None  # dict containing key 'pos' and 'arr_cached'
            self._geotransform = None
            self._projection = None
            self._shape = None
            self._dtype = None
            self._nodata = nodata
            self._mask_nodata = None
            self._mask_baddata = None
            self._footprint_poly = None
            self._gdalDataset_meta_already_set = False
            self._metadata = None
            self._bandnames = None

            if bandnames:
                self.bandnames = bandnames  # use property in order to validate given value
            if geotransform:
                self.geotransform = geotransform  # use property in order to validate given value
            if projection:
                self.projection = projection  # use property in order to validate given value

            if self.filePath:
                self.set_gdalDataset_meta()

    @property
    def arr(self):
        return self._arr

    @arr.setter
    def arr(self, ndarray):
        assert isinstance(ndarray, np.ndarray), "'arr' can only be set to a numpy array! Got %s." % type(ndarray)
        # assert ndarray.shape == self.shape, "'arr' can only be set to a numpy array with shape %s. Received %s. " \
        #                                    "If you need to change the dimensions, create a new instance of %s." \
        #                                    %(self.shape, ndarray.shape, self.__class__.__name__)
        #  THIS would avoid warping like this: geoArr.arr, geoArr.gt, geoArr.prj = warp(...)

        if ndarray.shape != self.shape:
            self.flush_cache()  # the cached array is not useful anymore

        self._arr = ndarray

    @property
    def bandnames(self):
        if self._bandnames and len(self._bandnames) == self.bands:
            return self._bandnames
        else:
            del self.bandnames  # runs deleter which sets it to default values
            return self._bandnames

    @bandnames.setter
    def bandnames(self, list_bandnames):
        # type: (list) -> None

        if list_bandnames:
            assert isinstance(list_bandnames, list), "A list must be given when setting the 'bandnames' attribute. " \
                                                     "Received %s." % type(list_bandnames)
            assert len(list_bandnames) == self.bands, \
                'Number of given bandnames does not match number of bands in array.'
            assert len(list(set([type(b) for b in list_bandnames]))) == 1 and type(list_bandnames[0] == 'str'), \
                "'bandnames must be a set of strings. Got other datetypes in there.'"
            bN_dict = OrderedDict((band, i) for i, band in enumerate(list_bandnames))
            assert len(bN_dict) == self.bands, \
                'Bands must not have the same name. Received band list: %s' % list_bandnames

            self._bandnames = bN_dict

            # update bandnames in metadata
            if self._metadata is not None:
                self.metadata.loc['band_name', :] = list_bandnames
        else:
            del self.bandnames

    @bandnames.deleter
    def bandnames(self):
        self._bandnames = OrderedDict(('B%s' % band, i) for i, band in enumerate(range(1, self.bands + 1)))
        if self._metadata is not None:
            self.metadata.loc['band_name', :] = list(self._bandnames.keys())

    @property
    def is_inmem(self):
        """Check if associated image array is completely loaded into memory."""

        return isinstance(self.arr, np.ndarray)

    @property
    def shape(self):
        """Get the array shape of the associated image array."""

        if self.is_inmem:
            return self.arr.shape
        else:
            if self._shape:
                return self._shape
            else:
                self.set_gdalDataset_meta()
                return self._shape

    @property
    def ndim(self):
        """Get the number dimensions of the associated image array."""
        return len(self.shape)

    @property
    def rows(self):
        """Get the number of rows of the associated image array."""

        return self.shape[0]

    @property
    def columns(self):
        """Get the number of columns of the associated image array."""

        return self.shape[1]

    cols = alias_property('columns')

    @property
    def bands(self):
        """Get the number of bands of the associated image array."""

        return self.shape[2] if len(self.shape) > 2 else 1

    @property
    def dtype(self):
        """Get the numpy data type of the associated image array."""

        if self._dtype:
            return self._dtype
        elif self.is_inmem:
            return self.arr.dtype
        else:
            self.set_gdalDataset_meta()
            return self._dtype

    @property
    def geotransform(self):
        """Get the GDAL GeoTransform of the associated image, e.g., (283500.0, 5.0, 0.0, 4464500.0, 0.0, -5.0)"""

        if self._geotransform:
            return self._geotransform
        elif not self.is_inmem:
            self.set_gdalDataset_meta()
            return self._geotransform
        else:
            return [0, 1, 0, 0, 0, -1]

    @geotransform.setter
    def geotransform(self, gt):
        assert isinstance(gt, (list, tuple)) and len(gt) == 6,\
            'geotransform must be a list with 6 numbers. Got %s.' % str(gt)

        for i in gt:
            assert is_number(i), "geotransform must contain only numbers. Got '%s' (type: %s)." % (i, type(i))

        self._geotransform = gt

    gt = alias_property('geotransform')

    @property
    def xgsd(self):
        """Get the X resolution in units of the given or detected projection."""

        return self.geotransform[1]

    @property
    def ygsd(self):
        """Get the Y resolution in units of the given or detected projection."""

        return abs(self.geotransform[5])

    @property
    def xygrid_specs(self):
        """
        Get the specifications for the X/Y coordinate grid, e.g. [[15,30], [0,30]] for a coordinate with its origin
        at X/Y[15,0] and a GSD of X/Y[15,30].
        """

        def get_grid(gt, xgsd, ygsd): return [[gt[0], gt[0] + xgsd], [gt[3], gt[3] - ygsd]]
        return get_grid(self.geotransform, self.xgsd, self.ygsd)

    @property
    def projection(self):
        """
        Get the projection of the associated image. Setting the projection is only allowed if GeoArray has been
        instanced from memory or the associated file on disk has no projection.
        """

        if self._projection:
            return self._projection
        elif not self.is_inmem:
            self.set_gdalDataset_meta()
            return self._projection  # or "LOCAL_CS[\"MAP\"]"
        else:
            return ''  # '"LOCAL_CS[\"MAP\"]"

    @projection.setter
    def projection(self, prj):
        if self.filePath:
            assert self.projection is None or prj_equal(self.projection, prj), \
                "Cannot set %s.projection to the given value because it does not match the projection from the file " \
                "on disk." % self.__class__.__name__
        else:
            self._projection = prj

    prj = alias_property('projection')

    @property
    def epsg(self):
        """Get the EPSG code of the projection of the GeoArray."""

        return WKT2EPSG(self.projection)

    @epsg.setter
    def epsg(self, epsg_code):
        self.projection = EPSG2WKT(epsg_code)

    @property
    def box(self):
        mapPoly = get_footprint_polygon(get_corner_coordinates(gt=self.geotransform, cols=self.columns, rows=self.rows))
        return boxObj(gt=self.geotransform, prj=self.projection, mapPoly=mapPoly)

    @property
    def nodata(self):
        """
        Get the nodata value of the GeoArray. If GeoArray has been instanced with a file path the file is checked
        for an existing nodata value. Otherwise (if no value is exlicitly given during object instanciation) the nodata
        value is tried to be automatically detected.
        """

        if self._nodata is not None:
            return self._nodata
        else:
            # try to get nodata value from file
            if not self.is_inmem:
                self.set_gdalDataset_meta()
            if self._nodata is None:
                self._nodata = self.find_noDataVal()
                if self._nodata == 'ambiguous':
                    warnings.warn('Nodata value could not be clearly identified. It has been set to None.')
                    self._nodata = None
                else:
                    if self._nodata is not None and not self.q:
                        print("Automatically detected nodata value for %s '%s': %s"
                              % (self.__class__.__name__, self.basename, self._nodata))
            return self._nodata

    @nodata.setter
    def nodata(self, value):
        self._nodata = value

    @property
    def mask_nodata(self):
        """
        Get the nodata mask of the associated image array. It is calculated using all image bands.
        """

        if self._mask_nodata is not None:
            return self._mask_nodata
        else:
            self.calc_mask_nodata()  # sets self._mask_nodata
            return self._mask_nodata

    @mask_nodata.setter
    def mask_nodata(self, mask):
        """Set bad data mask.

        :param mask:    Can be a file path, a numpy array or an instance o GeoArray.
        """

        if mask is not None:
            from .masks import NoDataMask
            geoArr_mask = NoDataMask(mask, progress=self.progress, q=self.q)
            geoArr_mask.gt = geoArr_mask.gt if geoArr_mask.gt not in [None, [0, 1, 0, 0, 0, -1]] else self.gt
            geoArr_mask.prj = geoArr_mask.prj if geoArr_mask.prj else self.prj
            imName = "the %s '%s'" % (self.__class__.__name__, self.basename)

            assert geoArr_mask.bands == 1, \
                'Expected one single band as nodata mask for %s. Got %s bands.' % (self.basename, geoArr_mask.bands)
            assert geoArr_mask.shape[:2] == self.shape[:2], 'The provided nodata mask must have the same number of ' \
                                                            'rows and columns as the %s itself.' % imName
            assert geoArr_mask.gt == self.gt, \
                'The geotransform of the given nodata mask for %s must match the geotransform of the %s itself. ' \
                'Got %s.' % (imName, self.__class__.__name__, geoArr_mask.gt)
            assert not geoArr_mask.prj or prj_equal(geoArr_mask.prj, self.prj), \
                'The projection of the given nodata mask for the %s must match the projection of the %s itself.' \
                % (imName, self.__class__.__name__)

            self._mask_nodata = geoArr_mask
        else:
            del self.mask_nodata

    @mask_nodata.deleter
    def mask_nodata(self):
        self._mask_nodata = None

    @property
    def mask_baddata(self):
        """
        Returns the bad data mask for the associated image array if it has been explicitly previously. It can be set
         by passing a file path, a numpy array or an instance of GeoArray to the setter of this property.
        """

        return self._mask_baddata

    @mask_baddata.setter
    def mask_baddata(self, mask):
        """Set bad data mask.

        :param mask:    Can be a file path, a numpy array or an instance o GeoArray.
        """

        if mask is not None:
            from .masks import BadDataMask
            geoArr_mask = BadDataMask(mask, progress=self.progress, q=self.q)
            geoArr_mask.gt = geoArr_mask.gt if geoArr_mask.gt not in [None, [0, 1, 0, 0, 0, -1]] else self.gt
            geoArr_mask.prj = geoArr_mask.prj if geoArr_mask.prj else self.prj
            imName = "the %s '%s'" % (self.__class__.__name__, self.basename)

            assert geoArr_mask.bands == 1, \
                'Expected one single band as bad data mask for %s. Got %s bands.' % (self.basename, geoArr_mask.bands)
            assert geoArr_mask.shape[:2] == self.shape[:2], 'The provided bad data mask must have the same number of ' \
                                                            'rows and columns as the %s itself.' % imName
            assert geoArr_mask.gt == self.gt, \
                'The geotransform of the given bad data mask for %s must match the geotransform of the %s itself. ' \
                'Got %s.' % (imName, self.__class__.__name__, geoArr_mask.gt)
            assert prj_equal(geoArr_mask.prj, self.prj), \
                'The projection of the given bad data mask for the %s must match the projection of the %s itself.' \
                % (imName, self.__class__.__name__)

            self._mask_baddata = geoArr_mask
        else:
            del self.mask_baddata

    @mask_baddata.deleter
    def mask_baddata(self):
        self._mask_baddata = None

    @property
    def footprint_poly(self):
        # FIXME should return polygon in image coordinates if no projection is available
        """
        Get the footprint polygon of the associated image array (returns an instance of shapely.geometry.Polygon.
        """

        if self._footprint_poly is None:
            assert self.mask_nodata is not None, 'A nodata mask is needed for calculating the footprint polygon. '
            if False not in self.mask_nodata[:]:
                # do not run raster2polygon if whole image is filled with data
                self._footprint_poly = self.box.mapPoly
            else:
                try:
                    multipolygon = raster2polygon(self.mask_nodata.astype(np.uint8), self.gt, self.prj, exact=False,
                                                  progress=self.progress, q=self.q, maxfeatCount=10, timeout=3)
                    self._footprint_poly = fill_holes_within_poly(multipolygon)
                except (RuntimeError, TimeoutError):
                    if not self.q:
                        warnings.warn("\nCalculation of footprint polygon failed for %s '%s'. Using outer bounds. One "
                                      "reason could be that the nodata value appears within the actual image (not only "
                                      "as fill value). To avoid this use another nodata value. Current nodata value is "
                                      "%s." % (self.__class__.__name__, self.basename, self.nodata))
                    self._footprint_poly = self.box.mapPoly

            # validation
            assert not polyVertices_outside_poly(self._footprint_poly, self.box.mapPoly), \
                "Computing footprint polygon for %s '%s' failed. The resulting polygon is partly or completely " \
                "outside of the image bounds." % (self.__class__.__name__, self.basename)
            # assert self._footprint_poly
            # for XY in self.corner_coord:
            #    assert self.GeoArray.box.mapPoly.contains(Point(XY)) or self.GeoArray.box.mapPoly.touches(Point(XY)), \
            #        "The corner position '%s' is outside of the %s." % (XY, self.imName)

        return self._footprint_poly

    @footprint_poly.setter
    def footprint_poly(self, poly):
        if isinstance(poly, Polygon):
            self._footprint_poly = poly
        elif isinstance(poly, str):
            self._footprint_poly = shply_loads(poly)
        else:
            raise ValueError("'footprint_poly' can only be set from a shapely polygon or a WKT string.")

    @property
    def metadata(self):
        """
        Returns a GeoDataFrame containing all available metadata (read from file if available).
        Use 'metadata[band_index].to_dict()' to get a metadata dictionary for a specific band.
        Use 'metadata.loc[row_name].to_dict()' to get all metadata values of the same key for all bands as dictionary.
        Use 'metadata.loc[row_name, band_index] = value' to set a new value.

        :return:  geopandas.GeoDataFrame
        """

        if self._metadata is not None:
            return self._metadata
        else:
            default = GeoDataFrame(columns=range(self.bands))
            # for bn,idx in self.bandnames.items():
            #    default.loc['band_index',bn] = idx
            self._metadata = default
            if not self.is_inmem:
                self.set_gdalDataset_meta()
                return self._metadata
            else:
                return self._metadata

    @metadata.setter
    def metadata(self, GDF):
        assert isinstance(GDF, (GeoDataFrame, DataFrame)) and len(GDF.columns) == self.bands, \
            "%s.metadata can only be set with an instance of geopandas.GeoDataFrame of which the column number " \
            "corresponds to the band number of %s." % (self.__class__.__name__, self.__class__.__name__)
        self._metadata = GDF

    meta = alias_property('metadata')

    def __getitem__(self, given):
        if isinstance(given, (int, float, slice)) and self.ndim == 3:
            # handle 'given' as index for 3rd (bands) dimension
            if self.is_inmem:
                return self.arr[:, :, given]
            else:
                return self.from_path(self.arg, [given])

        elif isinstance(given, str):
            # behave like a dictionary and return the corresponding band
            if self.bandnames:
                if given not in self.bandnames:
                    raise ValueError("'%s' is not a known band. Known bands are: %s"
                                     % (given, ', '.join(list(self.bandnames.keys()))))
                if self.is_inmem:
                    return self.arr if self.ndim == 2 else self.arr[:, :, self.bandnames[given]]
                else:
                    return self.from_path(self.arg, [self.bandnames[given]])
            else:
                raise ValueError('String indices are only supported if %s has been instanced with bandnames given.'
                                 % self.__class__.__name__)

        elif isinstance(given, (tuple, list)):
            # handle requests like geoArr[[1,2],[3,4]  -> not implemented in from_path if array is not in mem
            types = [type(i) for i in given]
            if list in types or tuple in types:
                self.to_mem()

            if len(given) == 3:

                # handle strings in the 3rd dim of 'given' -> convert them to a band index
                if isinstance(given[2], str):
                    if self.bandnames:
                        if given[2] not in self.bandnames:
                            raise ValueError("'%s' is not a known band. Known bands are: %s"
                                             % (given[2], ', '.join(list(self.bandnames.keys()))))

                        band_idx = self.bandnames[given[2]]
                        # NOTE: the string in the 3rd is ignored if ndim==2 and band_idx==0
                        if self.is_inmem:
                            return self.arr if (self.ndim == 2 and band_idx == 0) else self.arr[:, :, band_idx]
                        else:
                            getitem_params = \
                                given[:2] if (self.ndim == 2 and band_idx == 0) else given[:2] + (band_idx,)
                            return self.from_path(self.arg, getitem_params)
                    else:
                        raise ValueError(
                            'String indices are only supported if %s has been instanced with bandnames given.'
                            % self.__class__.__name__)

                # in case a third dim is requested from 2D-array -> ignore 3rd dim if 3rd dim is 0
                elif self.ndim == 2 and given[2] == 0:
                    if self.is_inmem:
                        return self.arr[given[:2]]
                    else:
                        return self.from_path(self.arg, given[:2])

        # if nothing has been returned until here -> behave like a numpy array
        if self.is_inmem:
            return self.arr[given]
        else:
            getitem_params = [given] if isinstance(given, slice) else given
            return self.from_path(self.arg, getitem_params)

    def __setitem__(self, idx, array2set):
        """Overwrites the pixel values of GeoArray.arr with the given array.

        :param idx:         <int, list, slice> the index position to overwrite
        :param array2set:   <np.ndarray> array to be set. Must be compatible to the given index position.
        :return:
        """

        if self.is_inmem:
            self.arr[idx] = array2set
        else:
            raise NotImplementedError('Item assignment for %s instances that are not in memory is not yet supported.'
                                      % self.__class__.__name__)

    def __getattr__(self, attr):
        # check if the requested attribute can not be present because GeoArray has been instanced with an array
        if attr not in self.__dir__() and not self.is_inmem and attr in ['shape', 'dtype', 'geotransform',
                                                                         'projection']:
            self.set_gdalDataset_meta()

        if attr in self.__dir__():  # __dir__() includes also methods and properties
            return self.__getattribute__(attr)  # __getattribute__ avoids infinite loop
        elif hasattr(np.array([]), attr):
            return self[:].__getattribute__(attr)
        else:
            raise AttributeError("%s object has no attribute '%s'." % (self.__class__.__name__, attr))

    def __getstate__(self):
        """Defines how the attributes of GMS object are pickled."""

        # clean array cache in order to avoid cache pickling
        self.flush_cache()

        return self.__dict__

    def __setstate__(self, state):
        """Defines how the attributes of GMS object are unpickled.
        NOTE: This method has been implemented because otherwise pickled and unpickled instances show recursion errors
        within __getattr__ when requesting any attribute.
        """

        self.__dict__ = state

    def calc_mask_nodata(self, fromBand=None, overwrite=False):
        """Calculates a no data mask with (values: 0=nodata; 1=data)

        :param fromBand:  <int> index of the band to be used (if None, all bands are used)
        :param overwrite: <bool> whether to overwrite existing nodata mask that has already been calculated
        :return:
        """

        if self._mask_nodata is None or overwrite:
            assert self.ndim in [2, 3], "Only 2D or 3D arrays are supported. Got a %sD array." % self.ndim
            arr = self[:, :, fromBand] if self.ndim == 3 and fromBand is not None else self[:]

            if self.nodata is None:
                self.mask_nodata = np.ones((self.rows, self.cols), np.bool)
            elif np.isnan(self.nodata):
                self.mask_nodata = \
                    np.invert(np.isnan(arr)) if arr.ndim == 2 else \
                    np.all(np.invert(np.isnan(arr)), axis=2)
            else:
                self.mask_nodata = \
                    np.ma.masked_not_equal(arr, self.nodata).mask if arr.ndim == 2 else \
                    np.all(np.ma.masked_not_equal(arr, self.nodata).mask, axis=2)

    def find_noDataVal(self, bandIdx=0, sz=3):
        """Tries to derive no data value from homogenious corner pixels within 3x3 windows (by default).
        :param bandIdx:
        :param sz: window size in which corner pixels are analysed
        """
        wins = [self[0:sz, 0:sz, bandIdx], self[0:sz, -sz:, bandIdx],
                self[-sz:, -sz:, bandIdx], self[-sz:, 0:sz, bandIdx]]  # UL, UR, LR, LL

        means, stds = [np.mean(win) for win in wins], [np.std(win) for win in wins]
        possVals = [mean for mean, std in zip(means, stds) if std == 0 or np.isnan(std)]
        # possVals==[]: all corners are filled with data; np.std(possVals)==0: noDataVal clearly identified

        if possVals:
            if np.std(possVals) != 0:
                if np.isnan(np.std(possVals)):
                    # at least one of the possible values is np.nan
                    nodata = np.nan
                else:
                    # different possible nodata values have been found in the image corner
                    nodata = 'ambiguous'
            else:
                if len(possVals) <= 2:
                    # each window in each corner
                    warnings.warn("\nAutomatic nodata value detection returned the value %s for GeoArray '%s' but this "
                                  "seems to be unreliable (occurs in only %s). To avoid automatic detection, just pass "
                                  "the correct nodata value."
                                  % (possVals[0], self.basename, ('2 image corners' if len(possVals) == 2 else
                                                                  '1 image corner')))
                nodata = possVals[0]
        else:
            nodata = None

        return nodata

    def set_gdalDataset_meta(self):
        """Retrieves GDAL metadata from file. This function is only executed once to avoid overwriting of user defined
         attributes, that are defined after object instanciation.

        :return:
        """

        if not self._gdalDataset_meta_already_set:
            assert self.filePath
            ds = gdal.Open(self.filePath)
            if not ds:
                raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

            # set private class variables (in order to avoid recursion error)
            self._shape = tuple([ds.RasterYSize, ds.RasterXSize] + ([ds.RasterCount] if ds.RasterCount > 1 else []))
            self._dtype = gdal_array.GDALTypeCodeToNumericTypeCode(ds.GetRasterBand(1).DataType)
            self._geotransform = list(ds.GetGeoTransform())

            # for some reason GDAL reads arbitrary geotransforms as (0, 1, 0, 0, 0, 1) instead of (0, 1, 0, 0, 0, -1)
            self._geotransform[5] = -abs(self._geotransform[5])  # => force ygsd to be negative

            # temp conversion to EPSG needed because GDAL seems to modify WKT string when writing file to disk
            # (e.g. using gdal_merge) -> conversion to EPSG and back undos that
            wkt = ds.GetProjection()
            self._projection = EPSG2WKT(WKT2EPSG(wkt)) if not isLocal(wkt) else ''

            if 'nodata' not in self._initParams or self._initParams['nodata'] is None:
                band = ds.GetRasterBand(1)
                # FIXME this does not support different nodata values within the same file
                self._nodata = band.GetNoDataValue()

            # read global domain metadata
            # TODO check to specifically use the 'ENVI' metadata domain ds.GetMetadata('ENVI')
            global_meta = ds.GetMetadata()

            # read band domain metadata
            for b in range(self.bands):
                band = ds.GetRasterBand(b + 1)
                meta_gs = GeoSeries(band.GetMetadata())

                # add band names if available
                if 'Band_%s' % str(b + 1) in global_meta.keys():
                    meta_gs['band_name'] = global_meta['Band_%s' % str(b + 1)]

                # TODO add the remaining global metadata

                # avoid double-call of set_gdalDataset_meta by setting self._metadata to default value
                self._metadata = \
                    self._metadata if self._metadata is not None else GeoDataFrame(columns=range(self.bands))

                # fill metadata
                self.metadata[b] = meta_gs
                del band

            del ds

        self._gdalDataset_meta_already_set = True

    def from_path(self, path, getitem_params=None):
        # type: (str, list) -> np.ndarray
        """Read a GDAL compatible raster image from disk, with respect to the given image position.
        NOTE: If the requested array position is already in cache, it is returned from there.

        :param path:            <str> the file path of the image to read
        :param getitem_params:  <list> a list of slices in the form [row_slice, col_slice, band_slice]
        :return out_arr:        <np.ndarray> the output array
        """

        ds = gdal.Open(path)
        if not ds:
            raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

        R, C, B = ds.RasterYSize, ds.RasterXSize, ds.RasterCount
        del ds

        # convert getitem_params to subset area to be read ##
        rS, rE, cS, cE, bS, bE, bL = [None] * 7

        # populate rS, rE, cS, cE, bS, bE, bL
        if getitem_params:
            if len(getitem_params) >= 2:
                givenR, givenC = getitem_params[:2]
                if isinstance(givenR, slice):
                    rS = givenR.start
                    rE = givenR.stop - 1 if givenR.stop is not None else None
                elif isinstance(givenR, int):
                    rS = givenR
                    rE = givenR
                if isinstance(givenC, slice):
                    cS = givenC.start
                    cE = givenC.stop - 1 if givenC.stop is not None else None
                elif isinstance(givenC, int):
                    cS = givenC
                    cE = givenC
            if len(getitem_params) in [1, 3]:
                givenB = getitem_params[2] if len(getitem_params) == 3 else getitem_params[0]
                if isinstance(givenB, slice):
                    bS = givenB.start
                    bE = givenB.stop - 1 if givenB.stop is not None else None
                elif isinstance(givenB, int):
                    bS = givenB
                    bE = givenB
                elif isinstance(givenB, (tuple, list)):
                    typesInGivenB = [type(i) for i in givenB]
                    assert len(list(set(typesInGivenB))) == 1, \
                        'Mixed data types within the list of bands are not supported.'
                    if isinstance(givenB[0], int):
                        bL = list(givenB)
                    elif isinstance(givenB[0], str):
                        bL = [self.bandnames[i] for i in givenB]
                elif type(givenB) in [str]:
                    bL = [self.bandnames[givenB]]

        # set defaults for not given values
        rS = rS if rS is not None else 0
        rE = rE if rE is not None else R - 1
        cS = cS if cS is not None else 0
        cE = cE if cE is not None else C - 1
        bS = bS if bS is not None else 0
        bE = bE if bE is not None else B - 1
        bL = list(range(bS, bE + 1)) if not bL else bL

        # convert negative to positive ones
        rS = rS if rS >= 0 else self.rows + rS
        rE = rE if rE >= 0 else self.rows + rE
        cS = cS if cS >= 0 else self.columns + cS
        cE = cE if cE >= 0 else self.columns + cE
        bS = bS if bS >= 0 else self.bands + bS
        bE = bE if bE >= 0 else self.bands + bE
        bL = [b if b >= 0 else (self.bands + b) for b in bL]

        # validate subset area bounds to be read
        def msg(v, idx, sz):
            # FIXME numpy raises that error ONLY for the 2nd axis
            return '%s is out of bounds for axis %s with size %s' % (v, idx, sz)

        for val, axIdx, axSize in zip([rS, rE, cS, cE, bS, bE], [0, 0, 1, 1, 2, 2], [R, R, C, C, B, B]):
            if not 0 <= val <= axSize - 1:
                raise ValueError(msg(val, axIdx, axSize))

        # summarize requested array position in arr_pos
        # NOTE: # bandlist must be string because truth value of an array with more than one element is ambiguous
        arr_pos = dict(rS=rS, rE=rE, cS=cS, cE=cE, bS=bS, bE=bE, bL=bL)

        # check if the requested array position is already in cache -> if yes, return it from there
        if self._arr_cache is not None and self._arr_cache['pos'] == arr_pos:
            out_arr = self._arr_cache['arr_cached']

        else:
            # TODO insert a multiprocessing.Lock here in order to prevent IO bottlenecks?
            # read subset area from disk
            if bL == list(range(0, B)):
                tempArr = gdalnumeric.LoadFile(path, cS, rS, cE - cS + 1, rE - rS + 1)
                out_arr = np.swapaxes(np.swapaxes(tempArr, 0, 2), 0, 1) if B > 1 else tempArr
                if out_arr is None:
                    raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
            else:
                ds = gdal.Open(path)
                if len(bL) == 1:
                    band = ds.GetRasterBand(bL[0] + 1)
                    out_arr = band.ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
                    if out_arr is None:
                        raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
                    del band
                else:
                    out_arr = np.empty((rE - rS + 1, cE - cS + 1, len(bL)))
                    for i, bIdx in enumerate(bL):
                        band = ds.GetRasterBand(bIdx + 1)
                        out_arr[:, :, i] = band.ReadAsArray(cS, rS, cE - cS + 1, rE - rS + 1)
                        if out_arr is None:
                            raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())
                        del band

                del ds

            # only set self.arr if the whole cube has been read (in order to avoid sudden shape changes)
            if out_arr.shape == self.shape:
                self.arr = out_arr

            # write _arr_cache
            self._arr_cache = dict(pos=arr_pos, arr_cached=out_arr)

        return out_arr  # TODO implement check of returned datatype (e.g. NoDataMask should always return np.bool
        # TODO -> would be np.int8 if an int8 file is read from disk

    def save(self, out_path, fmt='ENVI', creationOptions=None):
        # type: (str, str, list) -> None
        """Write the raster data to disk.

        :param out_path:        <str> output path
        :param fmt:             <str> the output format / GDAL driver code to be used for output creation, e.g. 'ENVI'
                                Refer to http://www.gdal.org/formats_list.html to get a full list of supported formats.
        :param creationOptions: <list> GDAL creation options,
                                e.g., ["QUALITY=80", "REVERSIBLE=YES", "WRITE_METADATA=YES"]
        """

        if not self.q:
            print('Writing GeoArray of size %s to %s.' % (self.shape, out_path))
        assert self.ndim in [2, 3], 'Only 2D- or 3D arrays are supported.'

        driver = gdal.GetDriverByName(fmt)
        if driver is None:
            raise Exception("'%s' is not a supported GDAL driver. Refer to www.gdal.org/formats_list.html for full "
                            "list of GDAL driver codes." % fmt)

        if not os.path.isdir(os.path.dirname(out_path)):
            os.makedirs(os.path.dirname(out_path))

        if self.is_inmem:
            ds = get_GDAL_ds_inmem(self.arr, self.geotransform, self.projection,
                                   self.nodata)  # expects rows,columns,bands

            # set metadata
            if not self.metadata.empty:
                global_meta = {}

                # set band domain metadata
                for bidx in range(self.bands):
                    band = ds.GetRasterBand(bidx + 1)
                    meta2write = self.metadata[bidx].to_dict()
                    meta2write = dict((k, v) for k, v in meta2write.items() if v is not np.nan)

                    if 'band_name' in meta2write:
                        global_meta['Band_%s' % str(bidx + 1)] = meta2write['band_name']
                        del meta2write['band_name']

                    band.SetMetadata(meta2write)
                    del band

                # set global domain metadata
                ds.SetMetadata(global_meta)

                # get ENVI metadata domain
                # ds_orig = gdal.Open(self.filePath)
                # envi_meta_domain = ds_orig.GetMetadata('ENVI')
                # ds.SetMetadata(envi_meta_domain, 'ENVI')
                # ds_orig = None

            driver.CreateCopy(out_path, ds, options=creationOptions if creationOptions else [])

            # rows, columns, bands => bands, rows, columns
            # out_arr = self.arr if self.ndim == 2 else np.swapaxes(np.swapaxes(self.arr, 0, 2), 1, 2)
            # gdalnumeric.SaveArray(out_arr, out_path, format=fmt, prototype=ds) # expects bands,rows,columns
            del ds

        else:
            src_ds = gdal.Open(self.filePath)
            if not src_ds:
                raise Exception('Error reading file:  ' + gdal.GetLastErrorMsg())

            gdal_Translate = get_gdal_func('Translate')
            gdal_Translate(out_path, src_ds, format=fmt, creationOptions=creationOptions)
            del src_ds

        if not os.path.exists(out_path):
            raise Exception(gdal.GetLastErrorMsg())

    def dump(self, out_path):
        # type: (str) -> None
        """Serialize the whole object instance to disk using dill."""

        import dill
        with open(out_path, 'wb') as outF:
            dill.dump(self, outF)

    def _get_plottable_image(self, xlim=None, ylim=None, band=None, boundsMap=None, boundsMapPrj=None, res_factor=None,
                             nodataVal=None, out_prj=None):
        # handle limits
        if boundsMap:
            boundsMapPrj = boundsMapPrj if boundsMapPrj else self.prj
            image2plot, gt, prj = self.get_mapPos(boundsMap, boundsMapPrj, band2get=band,
                                                  fillVal=nodataVal if nodataVal is not None else self.nodata)
        else:
            cS, cE = xlim if isinstance(xlim, (tuple, list)) else (0, self.columns)
            rS, rE = ylim if isinstance(ylim, (tuple, list)) else (0, self.rows)

            image2plot = self[rS:rE, cS:cE, band] if band is not None else self[rS:rE, cS:cE]
            gt, prj = self.geotransform, self.projection

        transOpt = ['SRC_METHOD=NO_GEOTRANSFORM'] if tuple(gt) == (0, 1, 0, 0, 0, -1) else None
        xdim, ydim = None, None
        nodataVal = nodataVal if nodataVal is not None else self.nodata

        if res_factor != 1. and image2plot.shape[0] * image2plot.shape[1] > 1e6:  # shape > 1000*1000
            # sample image down / normalize
            xdim, ydim = \
                (self.columns * res_factor, self.rows * res_factor) if res_factor else \
                tuple((np.array([self.columns, self.rows]) / (np.array([self.columns, self.rows]).max() / 1000)))
            xdim, ydim = int(xdim), int(ydim)

        if xdim or ydim or out_prj:
            from py_tools_ds.geo.raster.reproject import warp_ndarray
            image2plot, gt, prj = warp_ndarray(image2plot, self.geotransform, self.projection,
                                               out_XYdims=(xdim, ydim), in_nodata=nodataVal, out_nodata=nodataVal,
                                               transformerOptions=transOpt, out_prj=out_prj, q=True)
            if transOpt and 'NO_GEOTRANSFORM' in ','.join(transOpt):
                image2plot = np.flipud(image2plot)
                gt = list(gt)
                gt[3] = 0

            if xdim or ydim:
                print('Note: array has been downsampled to %s x %s for faster visualization.' % (xdim, ydim))

        return image2plot, gt, prj

    def show(self, xlim=None, ylim=None, band=None, boundsMap=None, boundsMapPrj=None, figsize=None,
             interpolation='none', vmin=None, vmax=None, pmin=2, pmax=98, cmap=None, nodataVal=None,
             res_factor=None, interactive=False):
        """Plots the desired array position into a figure.

        :param xlim:            [start_column, end_column]
        :param ylim:            [start_row, end_row]
        :param band:            the band index of the band to be plotted (if None and interactive==True all bands are
                                shown, otherwise the first band is chosen)
        :param boundsMap:       xmin, ymin, xmax, ymax
        :param boundsMapPrj:
        :param figsize:
        :param interpolation:
        :param vmin:            darkest pixel value to be included in stretching
        :param vmax:            brightest pixel value to be included in stretching
        :param pmin:            percentage to be used for excluding the darkest pixels from stretching (default: 2)
        :param pmax:            percentage to be used for excluding the brightest pixels from stretching (default: 98)
        :param cmap:
        :param nodataVal:
        :param res_factor:      <float> resolution factor for downsampling of the image to be plotted in order to save
                                plotting time and memory (default=None -> downsampling is performed to 1000x1000)
        :param interactive:     <bool> activates interactive plotting based on 'holoviews' library.
                                NOTE: this deactivates the magic '% matplotlib inline' in Jupyter Notebook
        :return:
        """

        band = (band if band is not None else 0) if not interactive else band

        # get image to plot
        nodataVal = nodataVal if nodataVal is not None else self.nodata
        image2plot, gt, prj = \
            self._get_plottable_image(xlim, ylim, band, boundsMap=boundsMap, boundsMapPrj=boundsMapPrj,
                                      res_factor=res_factor, nodataVal=nodataVal)

        # set color palette
        palette = cmap if cmap else plt.get_cmap('gray')
        if nodataVal is not None and np.std(image2plot) != 0:  # do not show nodata
            image2plot = np.ma.masked_equal(image2plot, nodataVal)
            vmin_auto, vmax_auto = \
                np.nanpercentile(image2plot.compressed(), pmin), np.nanpercentile(image2plot.compressed(), pmax)
            palette.set_bad('aqua', 0)
        else:
            vmin_auto, vmax_auto = np.nanpercentile(image2plot, pmin), np.nanpercentile(image2plot, pmax)

        vmin = vmin if vmin is not None else vmin_auto
        vmax = vmax if vmax is not None else vmax_auto

        palette.set_over('1')
        palette.set_under('0')

        # check availability of holoviews
        if not util.find_spec('holoviews'):
            warnings.warn("Interactive mode requires holoviews. Install it by running, e.g., "
                          "'conda install --yes -c ioam bokeh holoviews'. Using non-interactive mode.")
            interactive = False

        if interactive and image2plot.ndim == 3:
            import holoviews as hv
            from skimage.exposure import rescale_intensity
            hv.notebook_extension('matplotlib')

            cS, cE = xlim if isinstance(xlim, (tuple, list)) else (0, self.columns - 1)
            rS, rE = ylim if isinstance(ylim, (tuple, list)) else (0, self.rows - 1)

            image2plot = np.array(rescale_intensity(image2plot, in_range=(vmin, vmax)))

            def get_hv_image(b):
                # FIXME ylabels have the wrong order
                return hv.Image(image2plot[:, :, b] if b is not None else image2plot,
                                bounds=(cS, rS, cE, rE))(
                    style={'cmap': 'gray'}, plot={'fig_inches': 4 if figsize is None else figsize, 'show_grid': True})

            # hvIm = hv.Image(image2plot)(style={'cmap': 'gray'}, figure_inches=figsize)
            hmap = hv.HoloMap([(band, get_hv_image(band)) for band in range(image2plot.shape[2])], kdims=['band'])

            return hmap

        else:
            if interactive:
                warnings.warn('Currently there is no interactive mode for single-band arrays. '
                              'Switching to standard matplotlib figure..')  # TODO implement zoomable fig

            # show image
            plt.figure(figsize=figsize)
            rows, cols = image2plot.shape[:2]
            plt.imshow(image2plot, palette, interpolation=interpolation, extent=(0, cols, rows, 0),
                       vmin=vmin, vmax=vmax, )  # compressed excludes nodata values
            plt.show()

    def show_map(self, xlim=None, ylim=None, band=0, boundsMap=None, boundsMapPrj=None, ax=None, figsize=None,
                 interpolation='none', vmin=None, vmax=None, cmap=None, nodataVal=None, res_factor=None,
                 return_map=False, zoomable=False):
        """

        :param xlim:
        :param ylim:
        :param band:            band index (starting with 0)
        :param boundsMap:       xmin, ymin, xmax, ymax
        :param boundsMapPrj:
        :param ax:              allows to pass a matplotlib axis object where figure is plotted into
        :param figsize:
        :param interpolation:
        :param vmin:
        :param vmax:
        :param cmap:
        :param nodataVal:
        :param res_factor:      <float> resolution factor for downsampling of the image to be plotted in order to save
                                plotting time and memory (default=None -> downsampling is performed to 1000x1000)
        :param return_map:
        :param zoomable:        <bool> enable or disable zooming via mpld3
        :return:
        """

        if not util.find_spec('mpl_toolkits.basemap'):
            raise ImportError('This function requires Basemap. You need to install basemap manually (see www./'
                              'matplotlib.org/basemap) if you want to plot maps. It is not automatically installed.')

        from mpl_toolkits.basemap import Basemap

        mpld3_avl = util.find_spec('mpld3')
        if not mpld3_avl:
            warnings.warn('mpld3 is not available. Zooming disabled.')
            zoomable = False

        if zoomable:
            import mpld3
            mpld3.enable_notebook()
        elif mpld3_avl:
            import mpld3
            # noinspection PyBroadException
            try:
                mpld3.disable_notebook()
            except Exception:
                pass

        assert self.geotransform and tuple(self.geotransform) != (0, 1, 0, 0, 0, -1), \
            'A valid geotransform is needed for a map visualization. Got %s.' % list(self.geotransform)
        assert self.projection, "A projection is needed for a map visualization. Got '%s'." % self.projection

        # get image to plot
        nodataVal = nodataVal if nodataVal is not None else self.nodata
        image2plot, gt, prj = self._get_plottable_image(xlim, ylim, band, boundsMap=boundsMap,
                                                        boundsMapPrj=boundsMapPrj, res_factor=res_factor,
                                                        nodataVal=nodataVal, out_prj='epsg:4326')

        # calculate corner coordinates of plot
        # if boundsMap:
        #    boundsMapPrj = boundsMapPrj if boundsMapPrj else self.prj
        #    if not prj_equal(boundsMapPrj, 4326):
        #        boundsMap = reproject_shapelyGeometry(box(*boundsMap), boundsMapPrj, 4626).bounds
        #    xmin, ymin, xmax, ymax = boundsMap
        #    UL_XY, UR_XY, LR_XY, LL_XY = (xmin,ymax), (xmax, ymax), (xmax,ymin), (xmin, ymin)
        # else:
        UL_XY, UR_XY, LR_XY, LL_XY = [(YX[1], YX[0]) for YX in GeoArray(image2plot, gt, prj).box.boxMapYX]
        center_lon, center_lat = (UL_XY[0] + UR_XY[0]) / 2., (UL_XY[1] + LL_XY[1]) / 2.

        # create map
        fig = plt.figure(figsize=figsize)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05, wspace=0.15, hspace=0.05)
        ax = ax if ax is not None else plt.subplot(111)

        m = Basemap(projection='tmerc', resolution=None, lon_0=center_lon, lat_0=center_lat,
                    urcrnrlon=UR_XY[0], urcrnrlat=UR_XY[1], llcrnrlon=LL_XY[0], llcrnrlat=LL_XY[1])

        # set color palette
        palette = cmap if cmap else plt.get_cmap('gray')
        if nodataVal is not None and np.std(image2plot) != 0:  # do not show nodata
            image2plot = np.ma.masked_equal(image2plot, nodataVal)
            vmin_auto, vmax_auto = \
                np.nanpercentile(image2plot.compressed(), 2), np.nanpercentile(image2plot.compressed(), 98)
            palette.set_bad('aqua', 0)
        else:
            vmin_auto, vmax_auto = np.nanpercentile(image2plot, 2), np.nanpercentile(image2plot, 98)
        vmin = vmin if vmin is not None else vmin_auto
        vmax = vmax if vmax is not None else vmax_auto
        palette.set_over('1')
        palette.set_under('0')

        # add image to map (y-axis must be inverted for basemap)
        if zoomable:
            m.imshow(image2plot, palette, interpolation=interpolation, vmin=vmin, vmax=vmax)
        else:
            m.imshow(np.flipud(image2plot), palette, interpolation=interpolation, vmin=vmin, vmax=vmax)

        # add coordinate grid lines
        parallels = np.arange(-90, 90., 0.25)  # TODO make this adjustable
        # parallels = np.arange(-90, 90., 0.1)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=12, linewidth=0.4)

        meridians = np.arange(-180., 180., 0.25)
        # meridians = np.arange(-180., 180., 0.1)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=12, linewidth=0.4)

        if return_map:
            return fig, ax, m
        else:
            plt.show()

    def show_map_utm(self, xlim=None, ylim=None, band=0, figsize=None, interpolation='none', cmap=None,
                     nodataVal=None, vmin=None, vmax=None, res_factor=None, return_map=False):

        if not util.find_spec('mpl_toolkits.basemap'):
            raise ImportError('This function requires Basemap. You need to install basemap manually (see www./'
                              'matplotlib.org/basemap) if you want to plot maps. It is not automatically installed.')

        from mpl_toolkits.basemap import Basemap

        warnings.warn(UserWarning('This function is still under construction and may not work as expected!'))
        # TODO debug this function

        # get image to plot
        nodataVal = nodataVal if nodataVal is not None else self.nodata
        image2plot, gt, prj = self._get_plottable_image(xlim, ylim, band, res_factor, nodataVal)

        # calculate corner coordinates of plot
        box2plot = GeoArray(image2plot, gt, prj).box
        # UL_XY, UR_XY, LR_XY, LL_XY = [(YX[1], YX[0]) for YX in GeoArray(image2plot, gt, prj).box.boxMapYX]
        # Xarr, Yarr = self.box.get_coordArray_MapXY(prj=EPSG2WKT(4326))
        UL_XY, UR_XY, LR_XY, LL_XY = [transform_any_prj(self.projection, 'epsg:4326', x, y) for y, x in
                                      box2plot.boxMapYX]
        center_X, center_Y = (UL_XY[0] + UR_XY[0]) / 2., (UL_XY[1] + LL_XY[1]) / 2.
        center_lon, center_lat = transform_any_prj(prj, 'epsg:4326', center_X, center_Y)
        print(center_lon, center_lat)

        # create map
        fig = plt.figure(figsize=figsize)
        plt.subplots_adjust(left=0.05, right=0.95, top=0.90, bottom=0.05, wspace=0.15, hspace=0.05)
        ax = plt.subplot(111)
        print(UL_XY, UR_XY, LR_XY, LL_XY)
        #        m = Basemap(projection='tmerc', resolution=None, lon_0=center_lon, lat_0=center_lat,
        #                    urcrnrx=UR_XY[0], urcrnry=UR_XY[1], llcrnrx=LL_XY[0], llcrnry=LL_XY[1])
        m = Basemap(projection='tmerc', resolution=None, lon_0=center_lon, lat_0=center_lat,
                    urcrnrlon=UR_XY[0], urcrnrlat=UR_XY[1], llcrnrlon=LL_XY[0], llcrnrlat=LL_XY[1],
                    k_0=0.9996, rsphere=(6378137.00, 6356752.314245179), suppress_ticks=False)
        # m.pcolormesh(Xarr, Yarr, self[:], cmap=plt.cm.jet)

        # set color palette
        palette = cmap if cmap else plt.get_cmap('gray')
        if nodataVal is not None:  # do not show nodata
            image2plot = np.ma.masked_equal(image2plot, nodataVal)
            vmin_auto, vmax_auto = \
                np.nanpercentile(image2plot.compressed(), 2), np.nanpercentile(image2plot.compressed(), 98)
            palette.set_bad('aqua', 0)
        else:
            vmin_auto, vmax_auto = np.nanpercentile(image2plot, 2), np.nanpercentile(image2plot, 98)
        vmin = vmin if vmin is not None else vmin_auto
        vmax = vmax if vmax is not None else vmax_auto
        palette.set_over('1')
        palette.set_under('0')

        # add image to map (y-axis must be inverted for basemap)
        m.imshow(np.flipud(image2plot), palette, interpolation=interpolation, vmin=vmin, vmax=vmax)

        # add coordinate grid lines
        parallels = np.arange(-90, 90., 0.25)
        m.drawparallels(parallels, labels=[1, 0, 0, 0], fontsize=12, linewidth=0.4)

        meridians = np.arange(-180., 180., 0.25)
        m.drawmeridians(meridians, labels=[0, 0, 0, 1], fontsize=12, linewidth=0.4)

        if return_map:
            return fig, ax, m
        else:
            plt.show()

    def show_footprint(self):
        """This method is intended to be called from Jupyter Notebook and shows a web map containing the calculated
        footprint of GeoArray.
        """

        if not util.find_spec('folium') or not util.find_spec('geojson'):
            raise ImportError(
                "This method requires the libraries 'folium' and 'geojson'. They can be installed with "
                "the shell command 'pip install folium geojson'.")

        import folium
        import geojson

        lonlatPoly = reproject_shapelyGeometry(self.footprint_poly, self.epsg, 4326)

        m = folium.Map(location=tuple(np.array(lonlatPoly.centroid.coords.xy).flatten())[::-1])
        gjs = geojson.Feature(geometry=lonlatPoly, properties={})
        folium.GeoJson(gjs).add_to(m)
        return m

    def show_histogram(self, band=1, bins=200, normed=False, exclude_nodata=True, vmin=None, vmax=None, figsize=None):
        # type: (int, int, bool, bool, float, float, tuple) -> None

        """Show a histogram of a given band.

        :param band:            the band to be used to plot the histogram
        :param bins:            number of bins to plot (default: 200)
        :param normed:          whether to normalize the y-axis or not (default: False)
        :param exclude_nodata:  whether tp exclude nodata value from the histogram
        :param vmin:            minimum value for the x-axis of the histogram
        :param vmax:            maximum value for the x-axis of the histogram
        :param figsize:         figure size (tuple)
        """

        if self.nodata is not None and exclude_nodata:
            data = np.ma.masked_equal(self[band], self.nodata)
            data = data.compressed()
        else:
            data = self[band]

        vmin = vmin if vmin is not None else np.nanpercentile(data, 1)
        vmax = vmax if vmax is not None else np.nanpercentile(data, 99)
        image2plot = data

        plt.figure(figsize=figsize)
        plt.hist(list(image2plot.flat), normed=normed, bins=bins, color='gray', range=[vmin, vmax])
        plt.xlabel('Pixel value')
        plt.ylabel('Probabilty' if normed else 'Count')
        plt.show()

        if not self.q:
            print('STD:', np.std(data))
            print('MEAN:', np.mean(data))
            print('2 % percentile:', np.nanpercentile(data, 2))
            print('98 % percentile:', np.nanpercentile(data, 98))

    def clip_to_footprint(self):
        """Clip the GeoArray instance to the outer bounds of the actual footprint."""
        self.clip_to_poly(self.footprint_poly)

    def clip_to_poly(self, poly):
        """Clip the GeoArray instance to the outer bounds of a given shapely polygon.

        :param poly: instance of shapely.geometry.Polygon
        """
        # type: Polygon -> None
        self.arr, self.gt, self.projection = self.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
        self.mask_nodata.arr, self.mask_nodata.gt, self.mask_nodata.projection = \
            self.mask_nodata.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
        assert self.shape == self.mask_nodata.shape

        if self._mask_baddata is not None:
            self.mask_baddata.arr, self.mask_baddata.gt, self.mask_baddata.projection = \
                self.mask_baddata.get_mapPos(mapBounds=poly.bounds, mapBounds_prj=self.prj)
            assert self.shape == self.mask_baddata.shape

        # update footprint polygon
        if self._footprint_poly:
            if not (self.footprint_poly.within(self.box.mapPoly) or self.footprint_poly.equals(self.box.mapPoly)):
                self.footprint_poly = self.footprint_poly.intersection(self.box.mapPoly)

    def tiles(self, tilesize=(100, 100)):
        # type: (tuple) -> GeneratorLen
        """Get tiles of the full dataset in the given tile size.

        :param tilesize:    target size of the tiles (rows, columns)
                            NOTE: If rows or columns are None, all rows/columns are returned
        :return:            Generator with elements like: (((rowStart, rowEnd), (colStart, colEnd)), tiledata)
        """
        bounds_alltiles = get_array_tilebounds(self.shape, tilesize)

        class GeneratorLen(object):
            """Generator class adding __len__."""
            def __init__(self, gen, length):
                self.gen = gen
                self.length = length

            def __len__(self):
                return self.length

            def __iter__(self):
                return self.gen

        out_gen = ((((rS, rE), (cS, cE)), self[rS: rE + 1, cS: cE + 1, :]) for (rS, rE), (cS, cE) in bounds_alltiles)

        return GeneratorLen(out_gen, length=len(bounds_alltiles))

    def get_mapPos(self, mapBounds, mapBounds_prj, band2get=None, out_prj=None, arr_gt=None, arr_prj=None, fillVal=None,
                   rspAlg='near', progress=None, v=False):  # TODO implement slice for indexing bands
        # type: (tuple, str, int, str, tuple, str, int, str, bool, bool) -> (np.ndarray, tuple, str)
        """Returns the array data of GeoArray at a given geographic position.

        NOTE: The given mapBounds are snapped to the pixel grid of GeoArray. If the given mapBounds include areas
        outside of the extent of GeoArray, these areas are filled with the fill value of GeoArray.

        :param mapBounds:       xmin, ymin, xmax, ymax
        :param mapBounds_prj:   WKT projection string corresponding to mapBounds
        :param band2get:        band index of the band to be returned (full array if not given)
        :param out_prj:         output projection as WKT string. If not given, the self.projection is used.
        :param arr_gt:          GDAL GeoTransform (taken from self if not given)
        :param arr_prj:         WKT projection string (taken from self if not given)
        :param fillVal:         nodata value
        :param rspAlg:          <str> Resampling method to use. Available methods are:
                                near, bilinear, cubic, cubicspline, lanczos, average, mode, max, min, med, q1, q2
        :param progress:        whether to show progress bars or not
        :param v:               verbose mode (not related to GeoArray.v; must be explicitly set)
        :return:
        """
        arr_gt = arr_gt or self.geotransform
        arr_prj = arr_prj or self.projection
        out_prj = out_prj or arr_prj
        fillVal = fillVal if fillVal is not None else self.nodata
        progress = progress if progress is not None else self.progress

        if self.is_inmem and (not arr_gt or not arr_prj):
            raise ValueError('In case of in-mem arrays the respective geotransform and projection of the array '
                             'has to be passed.')

        if v:
            print('%s.get_mapPos() input parameters:')
            print('\tmapBounds', mapBounds, '<==>', self.box.boundsMap)
            print('\tEPSG', WKT2EPSG(mapBounds_prj), self.epsg)
            print('\tarr_gt', arr_gt, self.gt)
            print('\tarr_prj', WKT2EPSG(arr_prj), self.epsg)
            print('\tfillVal', fillVal, self.nodata, '\n')

        sub_arr, sub_gt, sub_prj = get_array_at_mapPos(self, arr_gt, arr_prj,
                                                       out_prj=out_prj,
                                                       mapBounds=mapBounds,
                                                       mapBounds_prj=mapBounds_prj,
                                                       fillVal=fillVal,
                                                       rspAlg=rspAlg,
                                                       out_gsd=(self.xgsd, self.ygsd),
                                                       band2get=band2get,
                                                       progress=progress)
        return sub_arr, sub_gt, sub_prj

    def get_subset(self, xslice=None, yslice=None, zslice=None, return_GeoArray=True, reset_bandnames=False):
        # type: (slice, slice, slice, bool) -> GeoArray
        """Returns a new instance of GeoArray representing a subset of the initial one wit respect to given array position.

        :param xslice:          a slice providing the X-position for the subset in the form slice(xstart, xend, xstep)
        :param yslice:          a slice providing the Y-position for the subset in the form slice(ystart, yend, ystep)
        :param zslice:          a slice providing the Z-position for the subset in the form slice(zstart, zend, zstep)
        :param return_GeoArray: whether to return an instance of GeoArray (default) or a tuple(np.ndarray, gt, prj)
        :param reset_bandnames: whether band names of subset should be copied from source GeoArray or reset to
                                'B1', 'B2', 'B3', ...
        :return:
        """

        sub_arr = self[yslice if yslice else slice(None),  # row
                       xslice if xslice else slice(None),  # col
                       zslice if zslice else slice(None)]  # band

        if sub_arr is None:
            raise ValueError('Unable to return an array for the given slice parameters.')

        sub_ulXY = imXY2mapXY((xslice.start or 0, yslice.start or 0), self.gt)
        sub_gt = (sub_ulXY[0], self.gt[1], self.gt[2], sub_ulXY[1], self.gt[4], self.gt[5])

        # apply zslice to bandnames and metadata
        if zslice:
            bNs_out = list(np.array(list(self.bandnames))[zslice])
            meta_out = None if self._metadata is None else self.meta[list(np.array(range(self.bands))[zslice])]
        else:
            bNs_out = list(self.bandnames)
            meta_out = self.meta

        # get output GeoArray and copy some properties from the input GeoArray
        sub_gA = GeoArray(sub_arr, sub_gt, self.prj,
                          bandnames=bNs_out, nodata=self.nodata, progress=self.progress, q=self.q)
        sub_gA.meta = meta_out
        sub_gA.filePath = self.filePath

        if reset_bandnames:
            del sub_gA.bandnames  # also updates the respective row in self.meta

        return sub_gA if return_GeoArray else (sub_arr, sub_gt, self.prj)

        # import copy   # TODO implement that in order to include all previously set attribute values
        # sub_gA = copy.deepcopy(self)
        # print(type(sub_gA))
        # sub_gA.arr = self[xslice if xslice else slice(None),
        #                   yslice if yslice else slice(None),
        #                   zslice if zslice else slice(None)]
        # #sub_gA.deepcopy_array()
        # sub_ulXY = imXY2mapXY((xslice.start, yslice.start), self.gt)
        # sub_gA.gt = (sub_ulXY[0], self.gt[1], self.gt[2], sub_ulXY[1], self.gt[4], self.gt[5])
        #
        # return sub_gA if return_GeoArray else (sub_gA.arr, sub_gA.gt, sub_gA.prj)

    def reproject_to_new_grid(self, prototype=None, tgt_prj=None, tgt_xygrid=None, rspAlg='cubic', CPUs=None):
        """Reproject all array-like attributes to a given target grid.

        :param prototype:   <GeoArray> an instance of GeoArray to be used as pixel grid reference
        :param tgt_prj:     <str> WKT string of the projection
        :param tgt_xygrid:  <list> target XY grid, e.g. [[xmin,xmax], [ymax, ymin]] for the UL corner
        :param rspAlg:      <str, int> GDAL compatible resampling algorithm code
        :param CPUs:        <int> number of CPUs to use (default: None -> use all available CPUs)
        :return:
        """

        assert (tgt_prj and tgt_xygrid) or prototype, "Provide either 'prototype' or 'tgt_prj' and 'tgt_xygrid'!"
        tgt_prj = tgt_prj or prototype.prj
        tgt_xygrid = tgt_xygrid or prototype.xygrid_specs
        assert tgt_xygrid[1][0] > tgt_xygrid[1][1]

        # set target GSD
        tgt_xgsd, tgt_ygsd = abs(tgt_xygrid[0][0] - tgt_xygrid[0][1]), abs(tgt_xygrid[1][0] - tgt_xygrid[1][1])

        # set target bounds
        tgt_bounds = reproject_shapelyGeometry(self.box.mapPoly, self.prj, tgt_prj).bounds

        gt = (tgt_xygrid[0][0], tgt_xgsd, 0, max(tgt_xygrid[1]), 0, -tgt_ygsd)
        xmin, ymin, xmax, ymax = snap_bounds_to_pixGrid(tgt_bounds, gt, roundAlg='on')

        from py_tools_ds.geo.raster.reproject import warp_ndarray
        self.arr, self.gt, self.prj = \
            warp_ndarray(self[:], self.gt, self.prj, tgt_prj,
                         out_gsd=(tgt_xgsd, tgt_ygsd),
                         out_bounds=(xmin, ymin, xmax, ymax),
                         out_bounds_prj=tgt_prj,
                         rspAlg=rspAlg,
                         in_nodata=self.nodata,
                         CPUs=CPUs,
                         progress=self.progress,
                         q=self.q)

        if hasattr(self, '_mask_nodata') and self._mask_nodata is not None:
            self.mask_nodata.reproject_to_new_grid(prototype=prototype,
                                                   tgt_prj=tgt_prj,
                                                   tgt_xygrid=tgt_xygrid,
                                                   rspAlg='near',
                                                   CPUs=CPUs)

        if hasattr(self, '_mask_baddata') and self._mask_baddata is not None:
            self.mask_baddata.reproject_to_new_grid(prototype=prototype,
                                                    tgt_prj=tgt_prj,
                                                    tgt_xygrid=tgt_xygrid,
                                                    rspAlg='near',
                                                    CPUs=CPUs)

        # update footprint polygon
        if self._footprint_poly:
            if not (self.footprint_poly.within(self.box.mapPoly) or self.footprint_poly.equals(self.box.mapPoly)):
                self.footprint_poly = self.footprint_poly.intersection(self.box.mapPoly)

    def read_pointData(self, mapXY_points, mapXY_points_prj=None, band=None):
        """Returns the array values for the given set of X/Y coordinates.
         NOTE: If GeoArray has been instanced with a file path, the function will read the dataset into memory.

        :param mapXY_points:        <np.ndarray, tuple> X/Y coordinates of the points of interest. If a numpy array is
                                    given, it must have the shape [Nx2]
        :param mapXY_points_prj:    <str, int> WKT string or EPSG code of the projection corresponding to the given
                                    coordinates.
        :param band:                <int> the band index of the band of interest. If None, the values of all bands are
                                    returned.
        :return:                    np.ndarray with shape [Nx2xbands]
        """

        mapXY = mapXY_points if isinstance(mapXY_points, np.ndarray) else np.array(mapXY_points).reshape(1, 2)
        prj = mapXY_points_prj if mapXY_points_prj else self.prj

        assert prj, 'A projection is needed for returning image DNs at specific map X/Y coordinates!'
        if not prj_equal(prj1=prj, prj2=self.prj):
            mapXY = transform_any_prj(prj, self.prj, mapXY[:, 0], mapXY[:, 1])

        imXY = mapXY2imXY(mapXY, self.geotransform)
        imYX = np.fliplr(np.array(imXY)).astype(np.int16)

        if imYX.size == 2:  # only one coordinate pair
            Y, X = imYX[0].tolist()
            return self[Y, X, band]
        else:  # multiple coordinate pairs
            return self[imYX.T.tolist() + [band]]

    def to_mem(self):
        """Reads the whole dataset into memory and sets self.arr to the read data."""

        self.arr = self[:]
        return self

    def to_disk(self):
        """Sets self.arr back to None if GeoArray has been instanced with a file path
        and the whole dataset has been read."""

        if self.filePath and os.path.isfile(self.filePath):
            self._arr = None
        else:
            warnings.warn('GeoArray object cannot be turned into disk mode because this asserts that GeoArray.filePath '
                          'contains a valid file path. Got %s.' % self.filePath)
        return self

    def deepcopy_array(self):
        if self.is_inmem:
            temp = np.empty_like(self.arr)
            temp[:] = self.arr
            self.arr = temp  # deep copy: converts view to its own array in order to avoid wrong output

    def cache_array_subset(self, arr_pos):
        # type: (list) -> None
        """Sets the array cache of the GeoArray instance to the given array in order to speed up calculations
        afterwards.

        :param arr_pos: a list of array indices as passed to __getitem__
        """

        if not self.is_inmem:
            # noinspection PyStatementEffect
            self[arr_pos]  # runs __getitem__ and sets self._arr_cache
        else:
            pass  # no array cache needed because array is in memory anyways

    def flush_cache(self):
        """Clear the array cache of the GeoArray instance."""

        self._arr_cache = None


def get_GeoArray_from_GDAL_ds(ds):
    # TODO implement as class method of GeoArray
    arr = gdalnumeric.DatasetReadAsArray(ds)
    if len(arr.shape) == 3:
        arr = np.swapaxes(np.swapaxes(arr, 0, 2), 0, 1)
    return GeoArray(arr, ds.GetGeoTransform(), ds.GetProjection())


class MultiGeoArray(object):  # pragma: no cover
    def __init__(self, GeoArray_list):
        """

        :param GeoArray_list:   a list of GeoArray instances having a geographic overlap
        """

        self._arrs = None

        self.arrs = GeoArray_list

        raise NotImplementedError('This class is not yet working.')  # FIXME

    @property
    def arrs(self):
        return self._arrs

    @arrs.setter
    def arrs(self, GeoArray_list):
        for geoArr in GeoArray_list:
            assert isinstance(geoArr, GeoArray), "'arrs' can only be set to a list of GeoArray instances."

        self._arrs = GeoArray_list
