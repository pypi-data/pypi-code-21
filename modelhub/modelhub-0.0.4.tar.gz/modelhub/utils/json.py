# -*- coding: utf-8 -*-
import json
import datetime
import uuid
import decimal
import numpy as np


class JSONEncoder(json.JSONEncoder):

    DATE_FORMAT = "%Y-%m-%d"
    TIME_FORMAT = "%H:%M:%S"

    @staticmethod
    def safe_new_datetime(d):
        kw = [d.year, d.month, d.day]
        if isinstance(d, datetime.datetime):
            kw.extend([d.hour, d.minute, d.second, d.microsecond, d.tzinfo])
        return datetime.datetime(*kw)

    @staticmethod
    def safe_new_date(d):
        return datetime.date(d.year, d.month, d.day)

    def default(self, o):
        if isinstance(o, np.ndarray):
            return o.tolist()
        if isinstance(o, np.floating):
            return float(o)
        if isinstance(o, np.integer):
            return int(o)
        if isinstance(o, bytes):
            return o.decode()
        if isinstance(o, set):
            return list(o)
        if isinstance(o, datetime.datetime):
            d = self.safe_new_datetime(o)
            return d.isoformat(" ")
        if isinstance(o, datetime.date):
            d = self.safe_new_date(o)
            return d.strftime(self.DATE_FORMAT)
        if isinstance(o, datetime.time):
            return o.strftime(self.TIME_FORMAT)
        if isinstance(o, datetime.timedelta):
            return o.total_seconds()
        if isinstance(o, decimal.Decimal):
            return str(o)
        if isinstance(o, uuid.UUID):
            return str(o)
        return super(JSONEncoder, self).default(o)


def dumps(*args, **kwargs):
    kwargs.setdefault("cls", JSONEncoder)
    return json.dumps(*args, **kwargs)


def dump(*args, **kwargs):
    kwargs.setdefault("cls", JSONEncoder)
    return json.dump(*args, **kwargs)


load = json.load

loads = json.loads
