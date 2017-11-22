from functools import partial
import warnings
from datetime import datetime, date, timedelta
import calendar
import json
import six

MSGPACK_INSTALLED = NUMPY_INSTALLED = PANDAS_INSTALLED = SJTS_SUPPORTS_NUMPY = SJTS_INSTALLED = False

try:
    import sjts

    SJTS_INSTALLED = True
    SJTS_SUPPORTS_NUMPY = sjts.__version__ >= '0.1.3'
    if not SJTS_SUPPORTS_NUMPY:
        warnings.warn('shooju-ts installed version does not support deserialization to numpy arrays')
except ImportError:
    sjts = None

try:
    import numpy

    NUMPY_INSTALLED = True
except ImportError:
    numpy = None

try:
    import pandas

    PANDAS_INSTALLED = True
except ImportError:
    pandas = None

try:
    import msgpack

    # otherwise will use default 'strict' encoding
    msgpack.loads = partial(msgpack.loads, encoding='utf-8')
    msgpack.dumps = partial(msgpack.dumps, encoding='utf-8')
    MSGPACK_INSTALLED = True
except ImportError:
    msgpack = None

try:
    # this is preferable way, but not all platforms supports negative unix timestamp
    datetime.utcfromtimestamp(-50000)  # test


    def milli_to_datetime(milli):
        """
        Converts millis to utc datetime

        :param int float milli: time in milliseconds
        :return:
        """
        return datetime.utcfromtimestamp(milli / 1000.)

except (ValueError, OSError):

    epoch = datetime(1970, 1, 1)


    def milli_to_datetime(milli):
        return epoch + timedelta(milliseconds=milli)


def to_milli(dt):
    """
    Date to utc time in milliseconds

    :param datetime.date datetime.datetime dt: date to be converted
    :return: the date as a milliseconds time string
    :rtype: str
    """
    if isinstance(dt, six.integer_types + (float,)):
        return dt
    elif not isinstance(dt, (datetime, date)):
        raise ValueError("You can pass milliseconds, datetime.date or datetime.datetime objects only")
    elif type(dt) is date:  # isinstance(datetime, date) is True
        dt = datetime(*dt.timetuple()[:3])

    return int(calendar.timegm(dt.utctimetuple())) * 1000


class JsonSerializer(object):
    __name__ = 'json'

    @staticmethod
    def loads(s, *args, **kwargs):
        return json.loads(s.decode('utf-8'), *args, **kwargs)

    @staticmethod
    def dumps(*args, **kwargs):
        return json.dumps(*args, **kwargs)


json_serializer = JsonSerializer()
