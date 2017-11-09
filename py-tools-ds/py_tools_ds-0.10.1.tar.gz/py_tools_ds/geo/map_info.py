# -*- coding: utf-8 -*-

from typing import Union  # noqa F401  # flake8 issue
try:
    from osgeo import osr
except ImportError:
    # noinspection PyPackageRequirements
    import osr

from .coord_trafo import transform_utm_to_wgs84

__author__ = "Daniel Scheffler"


def geotransform2mapinfo(gt, prj):
    # type: (Union[list, tuple, None], Union[str, None]) -> list
    """Builds an ENVI geo info from given GDAL GeoTransform and Projection (compatible with UTM and LonLat projections).
    :param gt:  GDAL GeoTransform, e.g. (249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0)
    :param prj: GDAL Projection - WKT Format
    :returns:   ENVI geo info, e.g. [ UTM , 1 , 1 , 256785.0 , 4572015.0 , 30.0 , 30.0 , 43 , North , WGS-84 ]
    :rtype:     list
    """

    if gt in [None, [0, 1, 0, 0, 0, -1], (0, 1, 0, 0, 0, -1)]:
        return ['Arbitrary', 1, 1, 0, 0, 1, 1, 0, 'North']

    if gt[2] != 0 or gt[4] != 0:  # TODO
        raise NotImplementedError('Currently rotated datasets are not supported.')

    UL_X, UL_Y, GSD_X, GSD_Y = gt[0], gt[3], gt[1], gt[5]

    srs = osr.SpatialReference()
    srs.ImportFromWkt(prj)

    if prj and not srs.IsLocal():
        Proj4 = [i[1:] for i in srs.ExportToProj4().split()]
        Proj4_proj = [v.split('=')[1] for i, v in enumerate(Proj4) if '=' in v and v.split('=')[0] == 'proj'][0]
        Proj4_ellps = \
            [v.split('=')[1] for i, v in enumerate(Proj4) if '=' in v and v.split('=')[0] in ['ellps', 'datum']][0]
        proj = 'Geographic Lat/Lon' if Proj4_proj == 'longlat' else 'UTM' if Proj4_proj == 'utm' else Proj4_proj
        ellps = 'WGS-84' if Proj4_ellps == 'WGS84' else Proj4_ellps

        def utm2wgs84(utmX, utmY): return transform_utm_to_wgs84(utmX, utmY, srs.GetUTMZone())

        def is_UTM_North_South(LonLat): return 'North' if LonLat[1] >= 0. else 'South'

        north_south = is_UTM_North_South(utm2wgs84(UL_X, UL_Y))
        map_info = [proj, 1, 1, UL_X, UL_Y, GSD_X, abs(GSD_Y), ellps] if proj != 'UTM' else \
            ['UTM', 1, 1, UL_X, UL_Y, GSD_X, abs(GSD_Y), srs.GetUTMZone(), north_south, ellps]
    else:
        map_info = ['Arbitrary', 1, 1, UL_X, UL_Y, GSD_X, abs(GSD_Y), 0, 'North']

    return map_info


def mapinfo2geotransform(map_info):
    # type: (Union[list, None]) -> list
    """Builds GDAL GeoTransform tuple from an ENVI geo info.

    :param map_info: ENVI geo info (list), e.g., ['UTM', 1, 1, 192585.0, 5379315.0, 30.0, 30.0, 41, 'North', 'WGS-84']
    :returns:        GDAL GeoTransform, e.g. [249885.0, 30.0, 0.0, 4578615.0, 0.0, -30.0]
    """
    if map_info:
        # FIXME rotated datasets are currently not supported -> function must return rotation at gt[2] and gt[4]
        # FIXME in case of rotated datasets: map info contains additional key: {... , rotation=1.0} --> ANGLE IN DEGREE
        # validate input map info
        exp_len = 10 if map_info[0] == 'UTM' else 9 if map_info[0] == 'Arbitrary' else 8
        assert isinstance(map_info, list) and len(map_info) == exp_len, \
            "The map info argument has to be a list of length %s. Got %s." % (exp_len, len(map_info))

        if map_info[1] == 1 and map_info[2] == 1:
            ULmapX, ULmapY = float(map_info[3]), float(map_info[4])
        else:
            ULmapX = float(map_info[3]) - (float(map_info[1]) * float(map_info[5]) - float(map_info[5]))
            ULmapY = float(map_info[4]) + (float(map_info[2]) * float(map_info[6]) - float(map_info[6]))

        return [ULmapX, float(map_info[5]), 0., ULmapY, 0., -float(map_info[6])]

    else:
        return [0, 1, 0, 0, 0, -1]


def get_corner_coordinates(gdal_ds=None, gt=None, cols=None, rows=None):
    """Returns (ULxy, LLxy, LRxy, URxy) in the same coordinate units like the given geotransform."""
    assert gdal_ds or (gt and cols and rows), \
        "GEOP.get_corner_coordinates: Missing argument! Please provide either 'gdal_ds' or 'gt', 'cols' AND 'rows'."

    gdal_ds_GT = gdal_ds.GetGeoTransform() if gdal_ds else gt
    ext = []
    xarr = [0, gdal_ds.RasterXSize if gdal_ds else cols]
    yarr = [0, gdal_ds.RasterYSize if gdal_ds else rows]

    for px in xarr:
        for py in yarr:
            x = gdal_ds_GT[0] + (px * gdal_ds_GT[1]) + (py * gdal_ds_GT[2])
            y = gdal_ds_GT[3] + (px * gdal_ds_GT[4]) + (py * gdal_ds_GT[5])
            ext.append([x, y])
        yarr.reverse()
    del gdal_ds_GT

    return ext
