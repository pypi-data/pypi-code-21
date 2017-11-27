# -*- coding: utf-8 -*-

import warnings
import numpy as np
from shapely.geometry import box, Polygon
from typing import TYPE_CHECKING, Union
from py_tools_ds.geo.coord_calc import get_corner_coordinates, calc_FullDataset_corner_positions
from py_tools_ds.geo.coord_grid import snap_bounds_to_pixGrid
from py_tools_ds.geo.coord_trafo import mapXY2imXY, transform_any_prj, imXY2mapXY
from py_tools_ds.geo.projection import prj_equal
from py_tools_ds.geo.vector.topology import get_overlap_polygon
from py_tools_ds.numeric.array import get_outFillZeroSaturated


__author__ = 'Daniel Scheffler'

if TYPE_CHECKING:
    from .baseclasses import GeoArray
    T_ndA_gA = Union[np.ndarray, GeoArray]


def _clip_array_at_mapPos(arr, mapBounds, arr_gt, band2clip=None, fillVal=0):
    # type: (T_ndA_gA, tuple, tuple, int, int) -> (np.ndarray, tuple)
    """
    NOTE: asserts that mapBounds have the same projection like the coordinates in arr_gt

    :param arr:
    :param mapBounds:   xmin, ymin, xmax, ymax
    :param arr_gt:
    :param band2clip:   band index of the band to be returned (full array if not given)
    :param fillVal:
    :return:
    """

    # assertions
    assert isinstance(arr_gt, (tuple, list))
    assert isinstance(band2clip, int) or band2clip is None

    # get array metadata
    rows, cols = arr.shape[:2]
    bands = arr.shape[2] if arr.ndim == 3 else 1
    arr_dtype = arr.dtype
    ULxy, LLxy, LRxy, URxy = get_corner_coordinates(gt=arr_gt, rows=rows, cols=cols)
    arrBounds = ULxy[0], LRxy[1], LRxy[0], ULxy[1]

    # snap mapBounds to the grid of the array
    mapBounds = snap_bounds_to_pixGrid(mapBounds, arr_gt)
    xmin, ymin, xmax, ymax = mapBounds

    # get out_gt and out_prj
    out_gt = list(arr_gt)
    out_gt[0], out_gt[3] = xmin, ymax

    # get image area to read
    cS, rS = [int(i) for i in mapXY2imXY((xmin, ymax), arr_gt)]  # UL
    cE, rE = [int(i) - 1 for i in mapXY2imXY((xmax, ymin), arr_gt)]  # LR

    if 0 <= rS <= rows - 1 and 0 <= rE <= rows - 1 and 0 <= cS <= cols - 1 and 0 <= cE <= cols - 1:
        """requested area is within the input array"""
        if bands == 1:
            out_arr = arr[rS:rE + 1, cS:cE + 1]
        else:
            out_arr = arr[rS:rE + 1, cS:cE + 1, band2clip] if band2clip is not None else arr[rS:rE + 1, cS:cE + 1, :]
    else:
        """requested area is not completely within the input array"""
        # create array according to size of mapBounds + fill with nodata
        tgt_rows = int(abs((ymax - ymin) / arr_gt[5]))
        tgt_cols = int(abs((xmax - xmin) / arr_gt[1]))
        tgt_bands = bands if band2clip is None else 1
        tgt_shape = (tgt_rows, tgt_cols, tgt_bands) if tgt_bands > 1 else (tgt_rows, tgt_cols)

        try:
            fillVal = fillVal if fillVal is not None else get_outFillZeroSaturated(arr)[0]
            out_arr = np.full(tgt_shape, fillVal, arr_dtype)
        except MemoryError:
            raise MemoryError('Calculated target dimensions are %s. Check your inputs!' % str(tgt_shape))

        # calculate image area to be read from input array
        overlap_poly = get_overlap_polygon(box(*arrBounds), box(*mapBounds))['overlap poly']
        assert overlap_poly, 'The input array and the requested geo area have no spatial overlap.'
        xmin_in, ymin_in, xmax_in, ymax_in = overlap_poly.bounds
        cS_in, rS_in = [int(i) for i in mapXY2imXY((xmin_in, ymax_in), arr_gt)]
        cE_in, rE_in = [int(i) - 1 for i in
                        mapXY2imXY((xmax_in, ymin_in), arr_gt)]  # -1 because max values do not represent pixel origins

        # read a subset of the input array
        if bands == 1:
            data = arr[rS_in:rE_in + 1, cS_in:cE_in + 1]
        else:
            data = arr[rS_in:rE_in + 1, cS_in:cE_in + 1, band2clip] if band2clip is not None else \
                arr[rS_in:rE_in + 1, cS_in:cE_in + 1, :]

        # calculate correct area of out_arr to be filled and fill it with read data from input array
        cS_out, rS_out = [int(i) for i in mapXY2imXY((xmin_in, ymax_in), out_gt)]
        # -1 because max values do not represent pixel origins
        cE_out, rE_out = [int(i) - 1 for i in mapXY2imXY((xmax_in, ymin_in), out_gt)]

        # fill newly created array with read data from input array
        if tgt_bands == 1:
            out_arr[rS_out:rE_out + 1, cS_out:cE_out + 1] = data if data.ndim == 2 else data[:, :, 0]
        else:
            out_arr[rS_out:rE_out + 1, cS_out:cE_out + 1, :] = data

    return out_arr, out_gt


def get_array_at_mapPosOLD(arr, arr_gt, arr_prj, mapBounds, mapBounds_prj, band2get=None,
                           fillVal=0):  # pragma: no cover
    # FIXME mapBounds_prj should not be handled as target projection
    """

    :param arr:
    :param arr_gt:
    :param arr_prj:
    :param mapBounds:       xmin, ymin, xmax, ymax
    :param mapBounds_prj:
    :param band2get:        band index of the band to be returned (full array if not given)
    :param fillVal:
    :return:
    """

    # [print(i,'\n') for i in [arr, arr_gt, arr_prj, mapBounds, mapBounds_prj]]
    # check if requested bounds have the same projection like the array
    samePrj = prj_equal(arr_prj, mapBounds_prj)

    if samePrj:
        out_prj = arr_prj
        out_arr, out_gt = _clip_array_at_mapPos(arr, mapBounds, arr_gt, band2clip=band2get, fillVal=fillVal)

    else:
        # calculate requested corner coordinates in the same projection like the input array
        # (bounds are not sufficient due to projection rotation)
        xmin, ymin, xmax, ymax = mapBounds
        ULxy, URxy, LRxy, LLxy = (xmin, ymax), (xmax, ymax), (xmax, ymin), (xmin, ymin)
        ULxy, URxy, LRxy, LLxy = [transform_any_prj(mapBounds_prj, arr_prj, *xy) for xy in [ULxy, URxy, LRxy, LLxy]]
        mapBounds_arrPrj = Polygon([ULxy, URxy, LRxy, LLxy]).buffer(arr_gt[1]).bounds

        # read subset of input array as temporary data (that has to be reprojected later)
        temp_arr, temp_gt = _clip_array_at_mapPos(arr, mapBounds_arrPrj, arr_gt, band2clip=band2get, fillVal=fillVal)

        # eliminate no data area for faster warping
        try:
            oneBandArr = np.all(np.where(temp_arr == fillVal, 0, 1), axis=2) \
                if len(temp_arr.shape) > 2 else np.where(temp_arr == fillVal, 0, 1)
            corners = [(i[1], i[0]) for i in
                       calc_FullDataset_corner_positions(oneBandArr, assert_four_corners=False)]
            bounds = [int(i) for i in Polygon(corners).bounds]
            cS, rS, cE, rE = bounds

            temp_arr = temp_arr[rS:rE + 1, cS:cE + 1]
            temp_gt[0], temp_gt[3] = [int(i) for i in imXY2mapXY((cS, rS), temp_gt)]
        except Exception:
            warnings.warn('Could not eliminate no data area for faster warping. '
                          'Result will not be affected but processing takes a bit longer..')

        # from matplotlib import pyplot as plt
        # plt.figure()
        # plt.imshow(temp_arr[:,:])

        # calculate requested geo bounds in the target projection, snapped to the output array grid
        mapBounds = snap_bounds_to_pixGrid(mapBounds, arr_gt)
        xmin, ymin, xmax, ymax = mapBounds
        out_gt = list(arr_gt)
        out_gt[0], out_gt[3] = xmin, ymax
        out_rows = int(abs((ymax - ymin) / arr_gt[5]))
        # FIXME using out_gt and outRowsCols is a workaround for not beeing able to pass output extent in the OUTPUT
        # FIXME projection
        out_cols = int(abs((xmax - xmin) / arr_gt[1]))

        # reproject temporary data to target projection (the projection of mapBounds)
        from py_tools_ds.geo.raster.reproject import warp_ndarray
        out_arr, out_gt, out_prj = warp_ndarray(temp_arr, temp_gt, arr_prj, mapBounds_prj,
                                                in_nodata=fillVal, out_nodata=fillVal, out_gt=out_gt,
                                                outRowsCols=(out_rows, out_cols), outExtent_within=True,
                                                rsp_alg=0)  # FIXME resampling alg

    return out_arr, out_gt, out_prj


def get_array_at_mapPos(arr, arr_gt, arr_prj, out_prj, mapBounds, mapBounds_prj=None, out_gsd=None, band2get=None,
                        fillVal=0, rspAlg='near', progress=True):
    # type: (T_ndA_gA, tuple, str, str, tuple, str, tuple, int, int, str, bool) -> (np.ndarray, tuple, str)
    """

    :param arr:
    :param arr_gt:
    :param arr_prj:
    :param out_prj:         output projection as WKT string
    :param mapBounds:       xmin, ymin, xmax, ymax
    :param mapBounds_prj:   the projection of the given map bounds (default: output projection)
    :param out_gsd:         (X,Y)
    :param band2get:        band index of the band to be returned (full array if not given)
    :param fillVal:
    :param rspAlg:          <str> Resampling method to use. Available methods are:
                            near, bilinear, cubic, cubicspline, lanczos, average, mode, max, min, med, q1, q2
    :param progress:
    :return:
    """

    # check if reprojection is needed
    mapBounds_prj = mapBounds_prj if mapBounds_prj else out_prj
    samePrj = prj_equal(arr_prj, out_prj)

    if samePrj:
        # output array is requested in the same projection like input array => no reprojection needed

        # mapBounds are expected to have the same projection like the input array
        if not prj_equal(arr_prj, mapBounds_prj):
            xmin, ymin, xmax, ymax = mapBounds
            (xmin, ymin), (xmax, ymax) = \
                [transform_any_prj(mapBounds_prj, arr_prj, X, Y) for X, Y in [(xmin, ymin), (xmax, ymax)]]
            mapBounds = xmin, ymin, xmax, ymax

        out_prj = arr_prj
        out_arr, out_gt = _clip_array_at_mapPos(arr, mapBounds, arr_gt, band2clip=band2get, fillVal=fillVal)

    else:
        # output array is requested in another projection => reprojection needed

        # calculate requested geo bounds in the target projection, snapped to the output array grid
        mapBounds = snap_bounds_to_pixGrid(mapBounds, arr_gt)

        arr = arr[:, :, band2get] if band2get else arr[:]  # also converts GeoArray to numpy.ndarray

        from py_tools_ds.geo.raster.reproject import warp_ndarray
        out_arr, out_gt, out_prj = \
            warp_ndarray(arr, arr_gt, arr_prj, out_prj=out_prj, out_bounds=mapBounds, out_bounds_prj=mapBounds_prj,
                         in_nodata=fillVal, out_nodata=fillVal, rspAlg=rspAlg, out_gsd=out_gsd, progress=progress)

    return out_arr, out_gt, out_prj
