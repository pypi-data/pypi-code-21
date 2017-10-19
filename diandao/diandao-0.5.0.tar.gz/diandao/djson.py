# -*- coding: utf-8 -*-

import simplejson as pjson
from json import JSONEncoder
from datetime import datetime, time
import decimal


class JSON(JSONEncoder):

    @staticmethod
    def default(o):
        if hasattr(o, '__json__') and callable(getattr(o, '__json__')):
            return o.__json__()

        if hasattr(o, '__dict__'):
            return o.__dict__

        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")

        if isinstance(o, time):
            return o.strftime("%H:%M:%S")

        return "%s" % o

    @classmethod
    def stringify(cls, o, ensure_ascii=False, separators=(',', ':'), encoding='utf-8', **kws):
        return pjson.dumps(o, default=cls.default, use_decimal=True, ensure_ascii=ensure_ascii, separators=separators, encoding=encoding, **kws)

    @classmethod
    def parse(cls, str, **kws):
        return pjson.loads(str, **kws)

    @classmethod
    def dict(cls, o, **kws):
        return cls.parse(cls.stringify(o, **kws))
