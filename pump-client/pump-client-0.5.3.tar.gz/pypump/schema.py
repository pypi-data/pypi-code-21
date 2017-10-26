# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from marshmallow import Schema, validate
from marshmallow.fields import Integer, Boolean, String, Raw, Nested, List

ALLOWED_OPS = [
    'or',
    '==',
    '!=',
    '>',
    '>=',
    '<',
    '<=',
    'range',  # between start (value[0]) and end (value[1])
    'in',  # one of
    '~in',  # not one of
    '^',  # starts with
    'i^',
    '~^',  # not starts with
    '~i^',
    'has',  # contains
    'ihas',
    '~has',  # not contains
    '~ihas',
    '$',  # ends with
    'i$',
    '~$',  # not ends with
    '~i$'
]


# sync with pump/pump/apischema.py


class MetricSchema(Schema):
    field = String(required=True, validate=[validate.Length(min=1)])
    aggregation = String()
    alias = String()


class FilterSchema(Schema):
    field = String(required=True, validate=[validate.Length(min=1)])
    operator = String(validate=[validate.OneOf(ALLOWED_OPS)])
    value = Raw(required=True)
    type = String()  # 用于类型转换


class SplitSchema(Schema):
    field = String(required=True)
    operator = String(validate=[validate.OneOf(['range', 'term'])])
    values = Raw(required=True)


class QuerySchema(Schema):
    ds_type = String(required=True)
    ds_dsn = String(required=True)
    table = String(required=True)
    metrics = Nested(MetricSchema, many=True)
    filters = Nested(FilterSchema, many=True)
    groupby = List(String(), default=[], missing=[])
    orderby = List(String(), default=[], missing=[])
    limit = Integer()
    splitby = Nested(SplitSchema)
    q = String(default='', missing='')
    cache_timeout = Integer(default=0, missing=0)
    force = Boolean(default=False, missing=False)


query_schema = QuerySchema()
