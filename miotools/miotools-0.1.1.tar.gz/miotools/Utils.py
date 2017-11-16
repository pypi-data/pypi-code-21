"""
Util Helper functions
"""
import time
from math import isclose
from datetime import timezone

DAY_OF_MILLISECONDS = 1000 * 60 * 60 * 24


# pylint: disable=too-few-public-methods
class ObjectView(object):
    """
    Convert a dictionary to object
    """
    def __init__(self, dict_def) -> None:
        self.__dict__ = dict_def


def get_current_millis():
    """
    Return Current millisecond
    :return:
    """
    return int(time.time() * 1000)


def get_utc_begin_millis(timestamp):
    """
    Return timestamp for beginning of the day
    :param timestamp:
    :return:
    """
    return int(timestamp / DAY_OF_MILLISECONDS) * DAY_OF_MILLISECONDS


def get_millis_seconds(date_time):
    """
    Get millisecond from datetimeObject
    :param date_time:
    :return:
    """
    return int(date_time.replace(tzinfo=timezone.utc).timestamp() * 1000)


def is_close(first, second):
    """
    compare float using 0.0001 accuracy
    :param first:
    :param second:
    :return:
    """
    return isclose(first, second, abs_tol=10**-4)
