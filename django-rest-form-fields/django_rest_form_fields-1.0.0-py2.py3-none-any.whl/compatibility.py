"""
This file contains functions for different python and django version compatibility
"""
from time import mktime

import datetime


def to_timestamp(dt):  # type: (datetime.datetime) -> int
    # dt.timestamp() does not work before python 3.3
    return mktime(dt.timetuple()) + dt.microsecond / 1e6
