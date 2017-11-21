#!/usr/bin/env python
# -*- coding: utf-8 -*-
from identifier import SimpleIdentifierCollection
from yosaipy2.core.serialize.serializer import BaseSchema
from marshmallow import fields, post_load
from collections import OrderedDict


class SimpleIdentifierSchema(BaseSchema):
    under_type = SimpleIdentifierCollection

    source_identifiers = fields.Dict(allow_none=True)
    primary_identifier = fields.String(allow_none=True)

    @post_load
    def make_identifier(self, data):
        s = SimpleIdentifierCollection()
        s.source_identifiers = OrderedDict(data['source_identifiers'])
        s._primary_identifier = data['primary_identifier']
        return s
