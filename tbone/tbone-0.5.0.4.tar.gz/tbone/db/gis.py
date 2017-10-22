#!/usr/bin/env python
# encoding: utf-8

from tbone.data.fields import StringField, ListField, FloatField

GEOTYPE_POINT = 'Point'
GEOTYPE_LINESTRING = 'LineString'
GEOTYPE_POLYGON = 'Polygon',
GEOTYPE_MULTI_POINT = 'MultiPoint'
GEOTYPE_MULTI_LINESTRING = 'MultiLineString'
GEOTYPE_MULTI_POLYGON = 'MultiPolygon'
GEOTYPE_GEOMETRY_COLLECTION = 'GeometryCollection'


from models import Model


class GeoBaseType(Model):
    type = StringField(choices=[
        GEOTYPE_POINT,
        GEOTYPE_LINESTRING,
        GEOTYPE_POLYGON,
        GEOTYPE_MULTI_POINT,
        GEOTYPE_MULTI_LINESTRING,
        GEOTYPE_GEOMETRY_COLLECTION
    ])


class GeoPointType(GeoBaseType):
    coordinates = ListField(FloatField)
