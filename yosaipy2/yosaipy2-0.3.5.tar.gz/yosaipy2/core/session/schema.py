#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import fields, post_load, pre_dump
from session import SimpleSession
from yosaipy2.core.serialize.serializer import BaseSchema
from yosaipy2.core.subject.schema import SimpleIdentifierSchema
from yosaipy2.core.utils.utils import get_logger

logger = get_logger()


class SimpleSessionSchema(BaseSchema):
    under_type = SimpleSession

    session_id = fields.String(allow_none=True)
    start_timestamp = fields.Integer(allow_none=True)
    stop_timestamp = fields.Integer(allow_none=True)
    last_access_time = fields.Integer(allow_none=True)
    idle_timeout = fields.Integer(allow_none=True)
    absolute_timeout = fields.Integer(allow_none=True)
    is_expired = fields.Boolean(allow_none=True)
    host = fields.String(allow_none=True)
    internal_attributes = fields.Dict(allow_none=True)
    attributes = fields.Dict(allow_none=True)

    @pre_dump
    def encode_attribute(self, data):
        # type:(SimpleSession) -> SimpleSession
        internal_attributes = data.internal_attributes
        if 'identifiers_session_key' not in internal_attributes:
            return data
        elif not internal_attributes['identifiers_session_key']:
            return data

        schema = SimpleIdentifierSchema()
        result = schema.dumps(internal_attributes['identifiers_session_key'])
        if result.errors:
            mesg = "encode internal attribute error: {}".format(result.errors)
            logger.error(mesg)
            raise Exception(mesg)
        internal_attributes['identifiers_session_key'] = result.data
        data.internal_attributes = internal_attributes
        return data

    @post_load
    def make_session(self, data):
        s = SimpleSession(data['absolute_timeout'], data['idle_timeout'], data['host'])
        for k in data:
            if hasattr(s, k):
                setattr(s, k, data[k])
        s.session_id = data['session_id']
        result = self._decode_internal(data['internal_attributes'])
        if not result:
            return s
        s.set_internal_attribute('identifiers_session_key', result)
        return s

    @staticmethod
    def _decode_internal(internal_attributes):
        if 'identifiers_session_key' not in internal_attributes:
            return None
        elif not internal_attributes['identifiers_session_key']:
            return None
        schema = SimpleIdentifierSchema()
        result = schema.loads(internal_attributes['identifiers_session_key'])
        if result.errors:
            mesg = "decode internal attributes error: {}".format(result.errors)
            logger.error(mesg)
            raise Exception(mesg)
        return result.data
