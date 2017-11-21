#!/usr/bin/env python
# -*- coding: utf-8 -*-
from abcs import Serializer
from marshmallow import Schema, fields, post_load, pre_dump, post_dump
from marshmallow import pre_load
from yosaipy2.core.utils.utils import json_loads
from yosaipy2.core.utils.utils import get_logger


class BaseSchema(Schema):
    schema_name = 'lSYx34'
    under_type = object

    @post_dump
    def add_schema(self, data):
        data[self.schema_name] = self.under_type.__name__

    @pre_load
    def del_schema(self, data):
        if self.schema_name in data:
            del data[self.schema_name]


class TypeWrapper(object):
    def __init__(self, data):
        self.data = data


class DictSchema(BaseSchema):
    data = fields.Dict(allow_none=True)
    under_type = dict

    @pre_dump
    def encode(self, data):
        return TypeWrapper(data)

    @post_load
    def decode(self, data):
        return data['data']


class ListSchema(DictSchema):
    under_type = list

    data = fields.List(fields.Dict(allow_none=True), allow_none=True)


class MarshmallowSerializer(Serializer):
    def __init__(self):
        self._schemas = {
            list.__name__: ListSchema,
            dict.__name__: DictSchema
        }
        self._logger = get_logger()

    def deserialize(self, data):
        data = json_loads(data)
        schema_name = data[BaseSchema.schema_name]
        schema_name = schema_name.encode('utf-8')
        schema = self._schemas[schema_name]()
        result = schema.load(data)
        if result.errors:
            self._logger.error("deserialize data failed: {}".format(result.errors))
            return None
        return result.data

    def serialize(self, obj):
        schema = self._schemas[obj.__class__.__name__]()
        result = schema.dumps(obj)
        if result.errors:
            self._logger.error("serialize data failed: {}".format(result.errors))
            return None
        return result.data

    def register_schema(self, cls, schema):
        self._schemas[cls.__name__] = schema

    @property
    def mimetype(self):
        return 'application/marshallow'
