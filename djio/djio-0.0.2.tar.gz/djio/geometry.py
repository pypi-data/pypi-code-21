#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: djio.geometry
.. moduleauthor:: Pat Daburu <pat@daburu.net>

Working with geometries?  Need help?  Here it is!
"""

from abc import ABCMeta, abstractmethod, abstractstaticmethod
from collections import namedtuple
from enum import Enum
from osgeo import ogr
from geoalchemy2.types import WKBElement, WKTElement
from geoalchemy2.shape import to_shape as to_shapely
from geoalchemy2.shape import from_shape as from_shapely
import math
from measurement.measures import Area, Distance
import re
from shapely.geometry.base import BaseGeometry
from shapely.geometry import Point as ShapelyPoint, LineString, LinearRing, Polygon as ShapelyPolygon
from shapely.wkb import dumps as dumps_wkb
from shapely.wkb import loads as loads_wkb
from shapely.wkt import dumps as dumps_wkt
from shapely.wkt import loads as loads_wkt
from typing import Dict, Callable, Optional, Set, Type


class GeometryException(Exception):
    """
    Raised when something goes wrong with a geometry.
    """
    def __init__(self, message: str, inner: Exception=None):
        """

        :param message: the exception message
        :param inner: the exception that caused this exception
        """
        super().__init__(message)
        self._inner = inner

    @property
    def inner(self) -> Exception:
        """
        Get the inner exception that caused this exception.
        """
        return self._inner

PointTuple = namedtuple('PointTuple', ['x', 'y', 'z', 'srid'])  #: a lightweight tuple that represents a point

LatLonTuple = namedtuple('LatLonTuple', ['latitude', 'longitude'])  #: a lightweight tuple that represents a location


class LateralSides(Enum):
    """
    This is a simple enumeration that identifies the lateral side of line (left or right).
    """
    LEFT = 'left'    #: the left side of the line
    RIGHT = 'right'  #: the right side of the line


class SpatialReference(object):
    """
    A spatial reference system (SRS) or coordinate reference system (CRS) is a coordinate-based local, regional or
    global system used to locate geographical entities. A spatial reference system defines a specific map projection,
    as well as transformations between different spatial reference systems.

    :seealso: https://en.wikipedia.org/wiki/Spatial_reference_system
    """
    _instances = {}  #: the instances of spatial reference that have been created
    _metric_linear_unit_names: Set[str] = set(['meter', 'metre'])  #: metric linear distance unit names

    def __init__(self, srid: int):
        """

        :param srid: the well-known spatial reference ID
        """
        # To coordinate __init__ with __new__, we're using a flag attribute that indicates to this instance that
        # even if __init__ is being called a second time, there's nothing more to do.
        if not hasattr(self, '_init'):
            self._init = True  # Mark this instance as "initialized".
            self._srid: int = srid  #: the spatial reference well-known ID
            # Keep a handy reference to OGR spatial reference.
            self._ogr_srs = self._get_ogr_sr(self._srid)
            self._is_metric = SpatialReference._ogr_is_metric(self._ogr_srs)

    def __new__(cls, srid: int):
        # If this spatial reference has already been created...
        if srid in SpatialReference._instances:
            # ...use the current instance.
            return SpatialReference._instances[srid]
        else:  # Otherwise, create a new instance.
            new_sr = super(SpatialReference, cls).__new__(cls)
            # Save it in the cache.
            SpatialReference._instances[srid] = new_sr
            # That's that.
            return new_sr

    @property
    def srid(self) -> int:
        """
        Get the spatial reference's well-known ID (srid).

        :return: the well-known spatial reference ID
        """
        return self._srid

    @property
    def is_metric(self) -> bool:
        """
        Is this a projected spatial reference system that measures linear units in single meters?

        :return: `true` if this is a projected spatial reference system that measures linear units in single meters
        """
        return self._is_metric

    @property
    def ogr_sr(self) -> ogr.osr.SpatialReference:
        """
        Get the OGR spatial reference.

        :return:  the OGR spatial reference
        """
        return self._ogr_srs

    @property
    def is_geographic(self) -> bool:
        """
        Is this spatial reference geographic?

        :return: `true` if this is a geographic spatial reference, otherwise `false`
        """
        return self._ogr_srs.IsGeographic() == 1

    @property
    def is_projected(self) -> bool:
        """
        Is this spatial reference projected?

        :return: `true` if this is a projected spatial reference, otherwise `false`
        """
        return self._ogr_srs.IsProjected() == 1

    @staticmethod
    def _ogr_is_metric(ogr_sr: ogr.osr.SpatialReference) -> bool:
        # If the coordinate system isn't projected...
        if ogr_sr.IsProjected() != 1:
            # ...it's not metric.
            return False
        # If the linear unit isn't one...
        if ogr_sr.GetLinearUnits() != 1.0:
            # ...it's not metric.
            return False
        # Get the linear unit name.
        linear_units_name: str = ogr_sr.GetLinearUnitsName()
        # If no linear unit name is supplied...
        if linear_units_name is None:
            # ...we can't claim this to be a "metric" spatial reference.
            return False
        # If we got this far, our final determination is based on whether or not we see the linear unit name in
        # set of names that mean "meter".
        return linear_units_name.lower() in SpatialReference._metric_linear_unit_names

    @staticmethod
    def from_srid(srid: int) -> 'SpatialReference':
        # If this spatial reference has already been created...
        if srid in SpatialReference._instances:
            # ...use the current instance.
            return SpatialReference._instances[srid]
        else:  # Otherwise, create a new instance.
            new_sr = SpatialReference(srid=srid)
            # Save it in the cache.
            SpatialReference._instances[srid] = new_sr
            # That's that.
            return new_sr

    @staticmethod
    def _get_ogr_sr(srid: int) -> ogr.osr.SpatialReference:
        """
        Get an OGR spatial reference from its spatial reference ID (srid).

        :param srid: the spatial reference ID
        :return: the OGR spatial reference.
        """
        # Create the OGR spatial reference.
        ogr_sr = ogr.osr.SpatialReference()
        # Let's assume the SRID is defined by the EPSG.
        # (Note: If we need to support others, this is the place to do it.)
        ogr_sr.ImportFromEPSG(srid)
        # That's that.
        return ogr_sr

    @staticmethod
    def get_utm_from_longitude(longitude: float) -> 'SpatialReference':
        zone = int(math.ceil(longitude + 180)/6)
        return SpatialReference.get_utm_for_zone(zone=zone)

    @staticmethod
    def get_utm_for_zone(zone: int) -> 'SpatialReference':
        utm_srid = int('269{zone}'.format(zone=zone))
        return SpatialReference.from_srid(srid=utm_srid)


class GeometryType(Enum):
    """
    These are the supported geometric data types.
    """
    UNKNOWN: int = 0   #: The geometry type is unknown.
    POINT: int = 1     #: a point geometry
    POLYLINE: int = 2  #: a polyline geometry
    POLYGON: int = 3   #: a polygon geometry

_shapely_geom_type_map: Dict[str, GeometryType] = {
    'point': GeometryType.POINT,
    'linestring': GeometryType.POLYLINE,
    'linearring': GeometryType.POLYLINE,
    'polygon' : GeometryType.POLYGON
}  #: maps Shapely geometry types to djio geometry types


_geometry_factory_functions: Dict[GeometryType, Callable[[BaseGeometry, SpatialReference], 'Geometry']] = {

}  #: a hash of GeometryTypes to functions that can create that type from a base geometry


class Geometry(object):
    """
    This is the common base class for all of the geometry types.
    """
    __metaclass__ = ABCMeta

    # This is a regex that matches an EWKT string, capturing the spatial reference ID (SRID) in a group called 'srid'
    # and the rest of the well-known text (WKT) in a group called 'wkt'.
    _ewkt_re = re.compile(
        r"srid=(?P<srid>\d+)\s*;\s*(?P<wkt>.*)",
        flags=re.IGNORECASE)  #: a regex that matches extended WKT (EWKT)

    def __init__(self,
                 shapely: BaseGeometry,
                 spatial_reference: SpatialReference or int=None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Keep that reference to the Shapely geometry.
        self._shapely: BaseGeometry = shapely
        # Let's figure out what the spatial reference is.  (It might be an instance of SpatialReference, or it might
        # be the SRID.)
        self._spatial_reference: SpatialReference = (spatial_reference
                                                     if isinstance(spatial_reference, SpatialReference)
                                                     else SpatialReference.from_srid(srid=spatial_reference))
        self._lazy_ogr_geometry: ogr.Geometry = None  #: an OGR geometry equivalent to this geometry, created lazily
        self._cached_transforms: Dict[int, Geometry] = {}  #: a cache of transformed geometries

    @property
    def geometry_type(self) -> GeometryType:
        try:
            return _shapely_geom_type_map[self._shapely.geom_type.lower()]
        except KeyError:
            return GeometryType.UNKNOWN

    @property
    def shapely(self) -> BaseGeometry:
        """
        Get the Shapely geometry underlying this geometry object.

        :return: the Shapely geometry
        """
        return self._shapely

    @property
    def spatial_reference(self) -> SpatialReference:
        """
        Get the geometry's spatial reference.

        :return: the geometry's spatial reference
        """
        return self._spatial_reference

    @property
    def to_ogr(self) -> ogr.Geometry:
        """
        Get the OGR geometry equivalent of this geometry.

        :return: the OGR geometry equivalent
        """
        # Create a new OGR geometry.  (We don't want one from the cache because we don't know what the caller will
        # do to it once we send it back.)
        return self._get_ogr_geometry(from_cache=False)

    def _get_ogr_geometry(self, from_cache: bool = True) -> ogr.Geometry:
        """
        Subclasses can use this method to get the OGR geometry equivalent.

        :param from_cache: Return the cached OGR geometry (if it's available).
        :return: the OGR geometry equivalent
        """
        # If we have already created the OGR geometry once, just return it again.
        if from_cache and self._lazy_ogr_geometry is not None:
            return self._lazy_ogr_geometry
        # Perform the WKB->OGR Geometry conversion.
        ogr_geometry: ogr.Geometry = ogr.CreateGeometryFromWkb(self._shapely.wkb)
        # Assign the spatial reference.
        ogr_geometry.AssignSpatialReference(self._spatial_reference.ogr_sr)
        # That's that!
        return ogr_geometry

    def transform(self, spatial_reference: SpatialReference or int) -> 'Geometry':
        """
        Create a new geometry based on this geometry but in another spatial reference.

        :param spatial_reference: the target spatial reference
        :return: the new transformed geometry
        """
        # Figure out the target spatial reference.
        sr: SpatialReference = (
            spatial_reference if isinstance(spatial_reference, SpatialReference)
            else SpatialReference.from_srid(srid=spatial_reference)
        )
        # If this geometry is already in the target spatial reference...
        if self.spatial_reference.srid == sr.srid:
            # ...no transformation is necessary.
            return self
        # If we've already transformed for this spatial reference once...
        if sr.srid in self._cached_transforms:
            # ...just return the previous product.
            return self._cached_transforms[sr.srid]
        else:
            # We need the OGR geometry.
            ogr_geometry = self._get_ogr_geometry(from_cache=True)
            # Transform the OGR geometry to the new coordinate system...
            ogr_geometry.TransformTo(sr.ogr_sr)
            # ...and build the new djio geometry from it.
            transformed_geometry = Geometry.from_ogr(ogr_geom=ogr_geometry)
            # Cache the shapely geometry in case somebody comes calling again.
            self._cached_transforms[sr.srid] = transformed_geometry
            # Now we can return it.
            return transformed_geometry

    def to_gml(self, version: int or str=3) -> str:
        """
        Export the geometry to GML.

        :param version: the desired GML version
        :return: the GML representation of the geometry
        """
        _ogr = self._get_ogr_geometry(from_cache=True)
        return _ogr.ExportToGML(options=[
            'FORMAT=GML{version}'.format(version=version)
        ])

    @abstractmethod
    def flip_coordinates(self) -> 'Geometry':
        """
        Create a geometry based on this one, but with the X and Y axis reversed.

        :return: a new :py:class:`Geometry` with reversed ordinals.
        """
        raise NotImplementedError('The subclass must implement this method.')

    @staticmethod
    def from_shapely(shapely: BaseGeometry,
                     spatial_reference:  SpatialReference or int) -> 'Geometry':
        """
        Create a new geometry based on a Shapely :py:class:`BaseGeometry`.

        :param shapely: the Shapely base geometry
        :param spatial_reference: the spatial reference (or spatial reference ID)
        :return: the new geometry
        :seealso:  :py:class:`Point`
        :seealso: :py:class:`Polyline`
        :seealso: :py:class:`Polygon`
        """
        # Get Shapely's version of the geometry type.  (Note that the keys in the dictionary are all lower-cased.)
        geometry_type: GeometryType = _shapely_geom_type_map[shapely.geom_type.lower()]
        # With this information, we can use the registered function to create the djio geometry.
        return _geometry_factory_functions[geometry_type](shapely, spatial_reference)

    @staticmethod
    def from_ogr(ogr_geom: ogr.Geometry, spatial_reference: SpatialReference or int=None) -> 'Geometry':
        # Grab the spatial reference from the arguments.
        _sr = spatial_reference
        # If the caller didn't provide one...
        if _sr is None:
            # ...dig it out of the geometry's spatial reference.
            ogr_srs: ogr.osr.SpatialReference = ogr_geom.GetSpatialReference()
            # Now, if the geometry didn't bring it's own spatial reference, we have a problem
            if ogr_srs is None:
                raise GeometryException('The geometry has no spatial reference, and no SRID was supplied.')
            _sr = int(ogr_srs.GetAttrValue('AUTHORITY', 1))
        return Geometry.from_wkb(wkb=ogr_geom.ExportToWkb(), spatial_reference=_sr)

    @staticmethod
    def from_ewkt(ewkt: str) -> 'Geometry':
        """
        Create a geometry from EWKT, a PostGIS-specific format that includes the spatial reference system identifier an
        up to four (4) ordinate values (XYZM).  For example: SRID=4326;POINT(-44.3 60.1) to locate a longitude/latitude
        coordinate using the WGS 84 reference coordinate system.

        :param ewkt: the extended well-known text (EWKT)
        :return: the geometry
        """
        # Let's see if we can match the format so we can separate the SRID from the rest of the WKT.
        ewkt_match = Geometry._ewkt_re.search(ewkt)
        if not ewkt_match:
            raise GeometryException('The EWKT is not properly formatted.')  # TODO: Add more information?
        # We have a match!  Let's go get the pieces.
        srid = int(ewkt_match.group('srid'))  # Grab the SRID.
        wkt = ewkt_match.group('wkt')  # Get the WKT.
        # Now we have enough information to create a Shapely geometry plus the SRID, so...
        return Geometry.from_wkt(wkt=wkt, spatial_reference=srid)

    @staticmethod
    def from_wkt(wkt: str, spatial_reference: SpatialReference or int) -> 'Geometry':
        shapely = loads_wkt(wkt)
        return Geometry.from_shapely(shapely=shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_wkb(wkb: str, spatial_reference: SpatialReference or int) -> 'Geometry':
        # https://geoalchemy-2.readthedocs.io/en/0.2.6/_modules/geoalchemy2/shape.html#to_shape
        shapely = loads_wkb(wkb)
        return Geometry.from_shapely(shapely=shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_gml(gml: str) -> 'Geometry':
        raise NotImplementedError('Coming soon...')

    @staticmethod
    def from_geoalchemy2(spatial_element: WKBElement or WKTElement,
                         srid: int) -> 'Geometry':
        shapely = to_shapely(spatial_element)
        return Geometry.from_shapely(shapely=shapely, srid=srid)


def _register_geometry_factory(geometry_type: GeometryType,
                               factory_function: Callable[[BaseGeometry, SpatialReference], Geometry]):
    """
    Register a geometry factory function.

    :param geometry_type: the enumerated geometry type
    :param factory_function: the factory function
    """
    _geometry_factory_functions[geometry_type] = factory_function


class Point(Geometry):
    """
    In modern mathematics, a point refers usually to an element of some set called a space.  More specifically, in
    Euclidean geometry, a point is a primitive notion upon which the geometry is built, meaning that a point cannot be
    defined in terms of previously defined objects. That is, a point is defined only by some properties, called axioms,
    that it must satisfy. In particular, the geometric points do not have any length, area, volume or any other
    dimensional attribute. A common interpretation is that the concept of a point is meant to capture the notion of a
    unique location in Euclidean space.
    """
    def __init__(self,
                 shapely: ShapelyPoint,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        # Redefine the shapely geometry (mostly to help out the IDEs).
        self._shapely: ShapelyPoint = None
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)
        self._lazy_point_tuple: PointTuple = None  #: a cached tuple representation of this point, created on demand
        self._lazy_latlon_tuple: LatLonTuple = None  #: a cached latitude/longitude tuple representation, created on demand

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POINT`
        """
        return GeometryType.POINT

    @property
    def x(self) -> float:
        """
        Get the X coordinate.

        :return: the X coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely.x

    @property
    def y(self) -> float:
        """
        Get the Y coordinate.

        :return: the Y coordinate
        """
        # noinspection PyUnresolvedReferences
        return self._shapely.y

    @property
    def z(self) -> float or None:
        """
        Get the Z coordinate.

        :return: the Z coordinate
        """
        return self._shapely.z

    def flip_coordinates(self) -> 'Point':
        """
        Create a point based on this one, but with the X and Y axis reversed.

        :return: a new :py:class:`Geometry` with reversed ordinals.
        """
        shapely: ShapelyPoint = ShapelyPoint(self._shapely.y, self._shapely.x)
        return Point(shapely=shapely, spatial_reference=self.spatial_reference)

    def to_point_tuple(self) -> PointTuple:
        """
        Get a lightweight tuple representation of this point.

        :return: the tuple representation of the point
        """
        # If we haven't created and cached the tuple...
        if self._lazy_point_tuple is None:
            # ...let's do that now.
            self._lazy_point_tuple = PointTuple(x=self.x, y=self.y, z=self.z, srid=self.spatial_reference.srid)
        # Return the cached tuple.
        return self._lazy_point_tuple

    def to_latlon_tuple(self) -> LatLonTuple:
        """
        Get a lightweight latitude/longitude tuple representation of this point.

        :return: the latitude/longitude tuple representation of this point
        """
        # If we haven't created and cached the tuple...
        if self._lazy_latlon_tuple is None:
            # We can use this point's coordinates directly if it's already in WGS84, otherwise we need to project it
            # first.
            p = self if self.spatial_reference.srid == 4326 else self.transform(spatial_reference=4326)
            self._lazy_latlon_tuple = LatLonTuple(latitude=p.y, longitude=p.x)
        # Return the cached tuple.
        return self._lazy_latlon_tuple

    @staticmethod
    def from_point_tuple(point_tuple: PointTuple) -> 'Point':
        """
        Create a point from a point tuple.

        :param point_tuple: the point tuple
        :return: the new point
        """
        p = Point.from_coordinates(x=point_tuple.x, y=point_tuple.y, spatial_reference=point_tuple.srid)
        # Go ahead and set the cached tuple property (since we have it right here).
        p._lazy_point_tuple = tuple
        # That's that.
        return p

    @staticmethod
    def from_latlon_tuple(latlon_tuple: LatLonTuple) -> 'Point':
        """
        Create a point from a latitude/longitude tuple.

        :param latlon_tuple: the latitude/longitude tuple
        :return: the new point
        """
        pt: PointTuple = PointTuple(x=latlon_tuple.longitude, y=latlon_tuple.latitude, srid=4326)
        return Point.from_point_tuple(pt)

    @staticmethod
    def from_lat_lon(latitude: float, longitude: float) -> 'Point':
        """
        Create a geometry from a set of latitude, longitude coordinates.

        :param latitude: the latitude
        :param longitude: the longitude
        :return: :py:class:`Point`
        """
        shapely = ShapelyPoint(longitude, latitude)
        return Point(shapely=shapely, spatial_reference=4326)

    @staticmethod
    def from_coordinates(x: float,
                         y: float,
                         spatial_reference: SpatialReference or int,
                         z: Optional[float]=None):
        """
        Create a point from its coordinates.

        :param x: the X coordinate
        :param y: the Y coordinate
        :param spatial_reference: the spatial reference (or spatial reference ID)
        :param z: the Z coordinate
        :return: the new :py:class:`Point`
        """
        shapely = ShapelyPoint(x, y, z) if z is not None else ShapelyPoint(x,y)
        return Point(shapely=shapely, spatial_reference=spatial_reference)

    @staticmethod
    def from_shapely(shapely: ShapelyPoint,
                     srid: int) -> 'Point':
        """
        Create a new point based on a Shapely point.

        :param shapely: the Shapely point
        :param srid: the spatial reference ID
        :return: the new geometry
        :seealso:  :py:func:`Geometry.from_shapely`
        """
        return Point(shapely=shapely, spatial_reference=srid)



    # TODO: Start adding Point-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POINT, Point)


class Polyline(Geometry):
    """
    In geometry, a polygonal chain is a connected series of line segments. More formally, a polygonal chain P is a curve
    specified by a sequence of points (A1 , A2, ... , An ) called its vertices. The curve itself consists of the line
    segments connecting the consecutive vertices. A polygonal chain may also be called a polygonal curve, polygonal
    path,  polyline,  piecewise linear curve, broken line or, in geographic information systems (that's us), a
    linestring or linear ring.
    """
    def __init__(self,
                 shapely: LineString or LinearRing,
                 spatial_reference: SpatialReference or int = None):
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYLINE`
        """
        return GeometryType.POLYLINE

    # TODO: Start adding Polyline-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYLINE, Polyline)


class Polygon(Geometry):
    """
    In elementary geometry, a polygon is a plane figure that is bounded by a finite chain of straight line segments
    closing in a loop to form a closed polygonal chain or circuit. These segments are called its edges or sides, and the
    points where two edges meet are the polygon's vertices (singular: vertex) or corners. The interior of the polygon is
    sometimes called its body.
    """
    def __init__(self,
                 shapely: ShapelyPolygon,
                 spatial_reference: SpatialReference or int = None):
        """

        :param shapely: a Shapely geometry
        :param spatial_reference: the geometry's spatial reference
        """
        super().__init__(shapely=shapely, spatial_reference=spatial_reference)

    @property
    def geometry_type(self) -> GeometryType:
        """
        Get the geometry type.

        :return:  :py:attr:`GeometryType.POLYGON`
        """
        return GeometryType.POLYGON

    def get_area(self, spatial_reference: Optional[SpatialReference or int]=None) -> Area:
        # TODO: This method is *ripe* for refactoring!
        sr = spatial_reference
        if sr is None:
            sr = SpatialReference.from_srid(3857)  # TODO: We can apply a more sophisticated mechanism here.
        elif not isinstance(spatial_reference, SpatialReference):
            sr = SpatialReference.from_srid(srid=spatial_reference)
        # Do a sanity check:  If the spatial reference isn't projected and measured in meters...
        if not sr.is_metric:
            raise GeometryException('The requested spatial reference is not projected, or is not metric.')
        # At this point, we know we're dealing with a metric projected coordinate system, so...
        if sr.srid == self.spatial_reference.srid:
            # ...we can just create the area.
            return Area(sq_m=self.shapely.area)
        else:
            # Otherwise, we need to transform the geometry to the target spatial reference, then get the area.
            return Area(sq_m=self.transform(spatial_reference).shapely.area)

    # TODO: Start adding Polygon-specific methods and properties.

# Register the geometry factory function (which is just the constructor).
_register_geometry_factory(GeometryType.POLYGON, Polygon)






