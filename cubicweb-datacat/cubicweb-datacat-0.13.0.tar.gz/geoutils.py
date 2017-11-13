# copyright 2016 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-datacat geo-spatial utilities."""


#
# Geometry helper functions
#


def srs_from_epsg(epsg):
    """Returns an ``osr.SpatialReference`` instance from the given EPSG code.

    Raises a ``ValueError`` if ``epsg`` is not a valid EPSG code.
    """
    from osgeo import osr
    srs = osr.SpatialReference()
    try:
        srs.ImportFromEPSG(int(epsg))
    except (TypeError, ValueError):
        raise ValueError('Invalid EPSG: {}'.format(epsg))
    return srs


def ogr_geom(value):
    """Returns an ``ogr.Geometry`` instance from the given value.

    Raises a ``ValueError`` if no geometry can be created from the given value.

    This function accepts values in the following formats:

    * (x, y) (2-uple of integers),
    * WKT,
    * GeoJSON.

    """
    from osgeo import ogr
    ogr.UseExceptions()  # See https://trac.osgeo.org/gdal/wiki/PythonGotchas
    if isinstance(value, (tuple, list)):  # Value has (x, y) format
        x, y = value
        geom = ogr.Geometry(ogr.wkbPoint)
        geom.SetCoordinateDimension(2)
        geom.AddPoint_2D(x, y)
        return geom
    for geom_function in [ogr.CreateGeometryFromWkt,  # Try in turn WKT, GeoJSON
                          ogr.CreateGeometryFromJson]:
        try:
            return geom_function(value)
        except RuntimeError:
            pass
    raise ValueError('Invalid value for Geometry: {}'.format(value))


# Checker function
# Needed until cubicweb-postgis does so by itself (see https://www.cubicweb.org/ticket/5629998)

def is_geometry(value, epsg=None, expected_geom_type=None, expected_epsg=None):
    """Returns ``True`` if the given value and srid are valid according to the expected parameters.
    """
    from osgeo import ogr
    ogr.UseExceptions()  # See https://trac.osgeo.org/gdal/wiki/PythonGotchas
    # Consider epsg
    if epsg is not None and not isinstance(epsg, int):
        return False
    if expected_epsg is not None and (epsg is None or epsg != expected_epsg):
        return False
    # Consider value
    try:  # Value must be WKT
        geom = ogr.CreateGeometryFromWkt(value)
        geom.IsValid()
    except RuntimeError:
        return False
    if expected_geom_type is not None \
            and geom.GetGeometryName().upper() != expected_geom_type.upper():
        return False
    return True


# Converter function
# Needed until cubicweb-postgis does so by itself (see https://www.cubicweb.org/ticket/5629998)

def geometry(value, epsg=None, expected_geom_type=None, expected_epsg=None):
    """Converts the given value according to the specified parameters, and returns a 2-uple
    ``(wkt, srid)`` suitable for cubicweb-postgis.

    The returned ``wkt`` is a string representing a geometry value in Well-Known Text (WKT) syntax,
    while ``srid`` is an integer identifying the spatial reference system in which lies ``wkt``.

    If the spatial reference system cannot be determined, returned ``srid`` is 0.

    Raises a ``ValueError`` if the given value cannot be converted to a valid ``Geometry``.

    Examples:

    .. code-block:: python

        >>> geometry('POINT (2 46)', expected_geom_type='MultiPoint')
        ('MULTIPOINT ((2 46))', 4326)

    .. code-block:: python

        >>> geometry('POINT (2 46)', expected_geom_type='GeometryCollection')
        ('GEOMETRYCOLLECTION (POINT (2 46))', 0)

    .. code-block:: python

        >>> geometry('POINT (2 46)', epsg=4326, expected_epsg=2154)
        ('POINT (622609.119992160820402 6544963.910583730787039)', 2154))

    .. code-block:: python

        >>> geometry('POINT (2 46)', expected_geom_type='LineString')
        Traceback (most recent call last):
          ...
        ValueError: Cannot convert 'POINT (2 46)' TO 'LINESTRING'

    """
    from osgeo import osr, ogr
    ogr.UseExceptions()  # See https://trac.osgeo.org/gdal/wiki/PythonGotchas
    _convert_to_multi_function = {
        'MULTIPOINT': ogr.ForceToMultiPoint,
        'MULTILINESTRING': ogr.ForceToMultiLineString,
        'MULTIPOLYGON': ogr.ForceToMultiPolygon,
    }
    # Create spatial reference systems from EPSGs
    srs = srs_from_epsg(epsg) if epsg is not None else None
    expected_srs = srs_from_epsg(expected_epsg) if expected_epsg is not None else None
    # Create geometry from value
    geom = ogr_geom(value)
    # Convert to expected type
    if expected_geom_type is not None:
        expected_geom_type = expected_geom_type.upper()
        geom_type = geom.GetGeometryName().upper()
        if geom_type == expected_geom_type:
            pass
        elif expected_geom_type.endswith(geom_type):  # Expect MULTITYPE and have TYPE
            geom = _convert_to_multi_function[expected_geom_type](geom)
        elif expected_geom_type == 'GEOMETRYCOLLECTION':
            geomc = ogr.Geometry(ogr.wkbGeometryCollection)
            geomc.AddGeometry(geom)
            geom = geomc
        else:
            raise ValueError('Cannot convert {} to {}'.format(value, expected_geom_type))
    # Reproject to expected spatial reference system
    if srs is not None:
        geom.AssignSpatialReference(srs)
    srs = geom.GetSpatialReference()  # May have been assigned elsewhere (eg. inline in GeoJSON)
    if expected_srs is not None:
        if srs is None:
            raise ValueError('Invalid or missing origin EPSG: {}'.format(epsg))
        if not srs.IsSame(expected_srs):
            transform = osr.CoordinateTransformation(srs, expected_srs)
            geom.Transform(transform)
            geom.AssignSpatialReference(expected_srs)
            srs = expected_srs
    # Return 2-uple
    srid = srs.GetAttrValue('Authority', 1) if srs is not None else None
    srid = int(srid) if srid is not None else 0
    return geom.ExportToWkt(), srid


#
# GeoJSON helper functions
#

def merge_in_geojson_collection(geojsons):
    """Return a new ``FeatureCollection`` GeoJSON object after merging all the objects in the given
    iterable.

    Return an empty object if both objects are empty too.

    Example:

    .. code-block:: python

        >>> geojson1 = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 46]}}
        >>> geosjon2 = {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 47]}}
        >>> merge = merge_geojson_features([geojson1, geosjon2])
        >>> type(merge)
        dict
        >>> merge['type']
        u'FeatureCollection'
        >>> len(merge['features'])
        2
        >>> merge['features'][0]
        {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 46]}}
        >>> merge['features'][1]
        {'type': 'Feature', 'geometry': {'type': 'Point', 'coordinates': [2, 47]}}

    As another example, merging a ``FeatureCollection`` with a ``Feature`` will append the
    ``Feature`` to list of features in the ``FeatureCollection``.
    """
    features = []
    for geojson in geojsons:
        if 'type' in geojson:
            if geojson['type'] == 'Feature':
                features.append(geojson)
            elif geojson['type'] == 'FeatureCollection':
                for feature in geojson['features']:
                    features.append(feature)
    if not features:
        return {}
    return {'type': u'FeatureCollection', 'features': features}
