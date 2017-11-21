#!/usr/bin/env python
# -*- coding: utf-8 -*-
from marshmallow import post_load
from session import WebSimpleSession
from yosaipy2.core.session.schema import SimpleSessionSchema


class WebSessionSchema(SimpleSessionSchema):
    under_type = WebSimpleSession

    @post_load
    def make_session(self, data):
        csrf_token = data['internal_attributes']['csrf_token']
        s = WebSimpleSession(
            csrf_token=csrf_token,
            absolute_timeout=data['absolute_timeout'],
            idle_timeout=data['idle_timeout'],
            host=data['host']
        )
        for k in data:
            if hasattr(s, k):
                setattr(s, k, data[k])
        result = self._decode_internal(data['internal_attributes'])
        if not result:
            return s
        s.set_internal_attribute('identifiers_session_key', result)
        return s
