# -*- coding: utf-8 -*-

from datetime import date, datetime, time
from json import JSONEncoder

from bson import ObjectId

# DATE_FORMAT = '%a, %d %b %Y %H:%M:%S GMT'
DATE_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'  # ISO 8601


def date_to_str(date_):
    """
    Converts a datetime value to the format defined in the configuration file.

    :param date: the datetime value to convert.
    """
    if isinstance(date_, str):
        return date_
    return datetime.strftime(date_, DATE_FORMAT) if date_ else None


def str_to_date(str_):
    """
    Converts a strinf to datetime

    :param str_: the string value to convert.
    """
    if isinstance(str_, datetime):
        return str_
    return datetime.strptime(str_, DATE_FORMAT) if str_ else None


class BaseJSONEncoder(JSONEncoder):

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, datetime):
            # convert any datetime to RFC 1123 format
            return date_to_str(obj)
        elif isinstance(obj, (time, date)):
            return obj.isoformat()
        elif isinstance(obj, set):
            return list(obj)
        return JSONEncoder.default(self, obj)


class MongoJSONEncoder(BaseJSONEncoder):

    def default(self, obj):  # pylint: disable=method-hidden
        if isinstance(obj, ObjectId):
            # BSON/Mongo ObjectId is rendered as a string
            return str(obj)
        else:
            # delegate rendering to base class method
            return super(MongoJSONEncoder, self).default(obj)
