import re
import socket
import time
from datetime import datetime, timedelta

import isodate as isodate
from es_wrapper.general.datatypes import format_data_recursively, convert_data_types

__author__ = 'guyeshet@gmail.com'

TIMESTAMP_FORMAT = '%Y-%m-%dT%H:%M:%S'
TIME_FORMAT = '%H:%M:%S'
NULL = "null"



def short_timestamp(timestamp):
    """
    Takes the timestamp format coming from WLC and converts it to the system native format for ES
    :param datetime.datetime timestamp:
    :return string:
    """
    if timestamp:
        out_format = "%B %d, %Y"
        return timestamp.strftime(out_format)
    else:
        return NULL


def long_timestamp(timestamp):
    if timestamp:
        in_format = '%Y-%m-%dT%H:%M:%SZ'
        return timestamp.strftime(in_format)
    else:
        return NULL


def ams_timestamp_change(timestamp):
    try:
        in_format = '%Y/%m/%d'
        timestamp = (datetime.strptime(timestamp, in_format))
        return format(timestamp, TIMESTAMP_FORMAT)
    except Exception as e:
        return 0

def check_timestamp_string(timestamp_str, timestamp_format=TIMESTAMP_FORMAT):
    """
    Returns true if the string is a valid timestamp
    :param timestamp_str: An input string with a timestamp to check
    :param timestamp_format: The format of timestamp to try and convert, default TIMESTAMP_FORMAT
    :return:
    """
    try:
        datetime.strptime(timestamp_str, timestamp_format)
        return True
    except ValueError:
        return False


def to_epoch(timestamp):
    """
    Returns the number of ms from epoch
    :param datetime.datetime() timestamp:
    :return int: Time from epoch
    """
    epoch = int(time.mktime(timestamp.timetuple())) * 1000
    return epoch


def convert_iso_timestamp_to_epoch(timestamp_str):
    """
    Converts ISO formatted timestamps
    :param timestamp_str:
    :return:
    """
    dt = isodate.parse_datetime(timestamp_str)
    return to_epoch(dt)


def from_epoch(epoch, divide_by_1000=True, timestamp=TIMESTAMP_FORMAT):
    """
    Convert the number of ms from epoch to timestamp
    :param epoch: number of ms from epoch
    :param bool divide_by_1000: Whether we need to divide the epoch number
    :param str timestamp: Which format to convert to
    :return timestamp: timestamp
    """
    epoch = convert_data_types(epoch)
    if divide_by_1000:
        return time.strftime(timestamp, time.gmtime(epoch/1000))
    else:
        return time.strftime(timestamp, time.gmtime(epoch))


def get_min_max_timestamps(interval_seconds, from_epoch=False, base_timestamp=None, max_is_now=True):
    """
    Return a tuple with both necessary timestamps
    :param integer interval_seconds: Number of seconds between min and max (max in default utcnow())
    :param bool from_epoch: A flag indicating whether to return timestamp in from_epoch values
    :param string base_timestamp: Used to change the timestamp reference from now() to the base timestamp
    :param bool max_is_now: If True, max_timestamp in current time, if False, min_timestamp in current time
    :return (max_timestamp, min_timestamp): The requested timestamps
    """
    # In case the timestamp reference is not utcnow()
    if base_timestamp:
        max_timestamp = change_timestamp(base_timestamp, interval_seconds)
        min_timestamp = base_timestamp
    else:
        if max_is_now:
            max_timestamp = current_utc_time(from_epoch=from_epoch)
            min_timestamp = current_utc_time(reduce_seconds=interval_seconds, from_epoch=from_epoch)
        else:
            max_timestamp = current_utc_time(add_seconds=interval_seconds, from_epoch=from_epoch)
            min_timestamp = current_utc_time(from_epoch=from_epoch)

    return min_timestamp, max_timestamp


def current_utc_time(add_seconds=0,
                     reduce_seconds=0,
                     from_epoch=False,
                     to_str=True,
                     template=TIMESTAMP_FORMAT,
                     iso_format=False):
    """
    Generates a timestamp in a string format
    :param int add_seconds: Seconds to add to utcnow()
    :param int reduce_seconds:Seconds to reduce from utcnow()
    :param bool from_epoch: A flag indicating whether to return timestamp in from_epoch values - Default False
    :param bool to_str: Convert all output values to strings - Default True
    :param template: A default time conversion template
    :param iso_format: Return an iso-formatted timestamp
    :return string/int/datetime.datetime() timestamp:
    """

    # create a timestamp for he inserted data - in UTC
    # timestamp = datetime.now(tz=pytz.utc) - timedelta(seconds=reduce_seconds) + timedelta(seconds=add_seconds)
    timestamp = datetime.utcnow() - timedelta(seconds=reduce_seconds) + timedelta(seconds=add_seconds)
    if iso_format:
        return timestamp.isoformat()

    # Return int from of ms from epoch
    if from_epoch:
        return to_epoch(timestamp)
    # Return a string of the timestamp
    if to_str:
        return format(timestamp, template)
    # Return original format
    return timestamp


def change_timestamp(base_timestamp, sec_to_add=0, to_str=True):
    """
    Getting a base timestamp as a string, converting it and adding seconds to it
    :param string base_timestamp: A timestamp to change
    :param int sec_to_add: Number of seconds to add to the timestamp
    :param to_str: Whether to return a string or not
    :return string : A new timestamp string
    """
    timestamp = (datetime.strptime(base_timestamp, TIMESTAMP_FORMAT))
    new_timestamp = timestamp + timedelta(seconds=sec_to_add)
    if to_str:
        return format(new_timestamp, TIMESTAMP_FORMAT)
    else:
        return new_timestamp


def extract_day_from_timestamp_string(timestamp_str):
    """
    Return a tuple of day, month, year
    :param timestamp_str:
    :return:
    """
    try:
        timestamp = (datetime.strptime(timestamp_str, TIMESTAMP_FORMAT))
    except Exception as e:
        timestamp = isodate.parse_datetime(timestamp_str)
    return timestamp.day, timestamp.month, timestamp.year


def check_if_timestamp_passed(timestamp_str, timeout=0):
    """
    This method converts a string timestamp to datetime and compares it to utcnow()
    :param string timestamp_str: The timestamp to compare
    :param int timeout: A timeout to add to the str to compare in to utcnow()
    :return bool: True if timestamp passed
    """
    if not timestamp_str:
        return False
    # Convert the timestamp and check if it pass the current time
    timestamp = (datetime.strptime(timestamp_str, TIMESTAMP_FORMAT))
    # Check if the current time is greater then the timestamp, plus the timeout for invalidation
    if datetime.utcnow() > timestamp + timedelta(seconds=timeout):
        return True
    else:
        return False


def convert_wlc_timestamp_format(orig_timestamp):
    """
    Takes the timestamp format coming from WLC and converts it to the system native format for ES
    :param string orig_timestamp:
    :return string:
    """
    timestamp = (datetime.strptime(orig_timestamp, "%c"))
    return format(timestamp, TIMESTAMP_FORMAT)


def generate_daily_index(index_name):
    """
    Returns an index name with the date at its tail
    :param index_name:
    :return:
    """
    return index_name + "-" + format(datetime.utcnow(), '%Y-%m-%d')


def type_formatter(data, to_str=False):
    """
    This method formats a dictionary or any data types and keeps only 3 digits after
    the do for floats.
    :param data:
    :param bool to_str: If True we convert all output values to string
    :return:
    """
    if to_str:
        return format_data_recursively(data, float_formatter, convert_to_string)
    else:
        return format_data_recursively(data, float_formatter)


def float_formatter(data):
    """
    Removes digits after dots and 1.0, 2.0
    :param data:
    :return:
    """
    if type(data) is float:
        data = '{0:g}'.format(float(data))
    return data


def convert_to_string(data):
    """
    This method converts floats and ints to string
    :param data:
    :return:
    """
    if (type(data) is float) or (type(data) is int):
        data = str(data)
    return data


def timeit(method):
    """
    Timeit decorator to determine functions runtime
    :param method:
    :return:
    """
    def timed(*args, **kw):
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        print ('%r (%r, %r) %2.2f sec' % (method.__name__, args, kw, te-ts))
        return result

    return timed


def convert_es_invalid_chars(data_str):
    """
    Replaces the ES chars we use just for saving
    :param data_str:
    :return:
    """
    if type(data_str) == str or type(data_str) == unicode:
        return data_str.replace("_", ":")
    else:
        return ""


def is_mac_address(data):
    """
    This method checks if a string is a real mac address
    :param str data:
    :return:
    """
    # if len(string) == (6*2+5) and mac_dev in string:
    # Check if the input data is a valid mac address
    if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", data.lower()):
        return True
    return False


def remove_non_digit_chars(string):
    """
    This method removes all non-digit chars
    :param str string:
    :return str:
    """
    if string:
        return re.sub("\D", "", string)


def parse_channel_string(data, sort_channel_list=False):
    """
    Removes all non digit chars
    :param string data: String with chars and numbers
    :param bool sort_channel_list: If True we return a sorted list of channels
    :return string data: String with digits only
    """
    channel_list = re.split(',|/|-', str(data))
    for i in range(len(channel_list)):
        channel_list[i] = remove_non_digit_chars(channel_list[i])

    # Return the lowest value
    if sort_channel_list:
        return sorted(channel_list)[0]
    else:
        return channel_list[0]


def is_ip_address(ip_address):
    """
    This method checks if a string is a valid IP V4 address
    :param str ip_address:
    :return:
    """
    try:
        socket.inet_aton(ip_address)
        return True
    except socket.error:
        return False


def get_list_len(data_list):
    """
    Wraps list len
    :param data_list:
    :return:
    """
    try:
        return len(data_list)
    except TypeError:
        return 0


def calculate_diff_value(val_a, val_b):
    """
    This method returns the diff between two values, as long as the first value is not zero
    :param val_a:
    :param val_b:
    :return:
    """
    if val_a != 0:
        return val_b - val_a
    else:
        return 0


def get_value_with_default(var_to_check, default):
    """
    Used when taking values from args of env vars
    :param var_to_check:
    :param default:
    :return:
    """
    if var_to_check:
        return var_to_check
    else:
        return default


def compare_timestamps(new_timestamp, curr_timestamp):
    """
    This method compares two different timestamps and returns true if one is larger then the other
    :param new_timestamp:
    :param curr_timestamp:
    :return boolean: if new if newer then current
    """
    # Remove spaces
    new_timestamp = new_timestamp.replace(" ", "")
    new_timestamp = new_timestamp.strip()
    curr_timestamp = curr_timestamp.replace(" ", "")
    curr_timestamp = curr_timestamp.strip()

    curr = datetime.strptime(curr_timestamp, TIMESTAMP_FORMAT)
    new = datetime.strptime(new_timestamp, TIMESTAMP_FORMAT)
    return new > curr


def letters_only(term):
    """
    Retains only letters in the string
    :param term:
    :return:
    """
    return re.sub('[^a-zA-Z]+', '', term)