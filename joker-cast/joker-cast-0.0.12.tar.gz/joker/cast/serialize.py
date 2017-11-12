#!/usr/bin/env python3
# coding: utf-8

from __future__ import division, print_function

import datetime
import json


class JSONEncoderExtended(json.JSONEncoder):
    def default(self, obj):
        if hasattr(obj, 'as_json_serializable'):
            return obj.as_json_serializable()
        datetime_types = datetime.datetime, datetime.time, datetime.time
        if isinstance(obj, datetime_types):
            return obj.isoformat()
        elif isinstance(obj, datetime.timedelta):
            return obj.total_seconds()
        else:
            return self.default(vars(obj))


def human_json_dumps(s, **kwargs):
    return json.dumps(s, indent=4, ensure_ascii=False,
                      cls=JSONEncoderExtended, **kwargs)
