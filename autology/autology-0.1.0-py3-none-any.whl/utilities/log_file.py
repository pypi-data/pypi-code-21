"""Utilities for helping with the markdown log files stored."""
import datetime

DEFAULT_EVENT_LENGTH = 60  # minutes


def get_start_time(date, front_matter, file_path=None):
    """
    Convert the details in front matter into a start time for the file.  If there isn't a value stored in the front
    matter data values, then if defined the file_path will be used.

    Will search for start_time key in the front matter dictionary, if that value is a string, then it will be parsed as:
    HH:MM.
    If it's an integer or a if it's a duration, then it will be parsed as [HH:]MM:SS duration value which is what YAML
    uses by default.  Please know that this is because of YAML parsing rules.

    if the front_matter doesn't contain a start_time and file_path is None, then the start_time will be returned as
    midnight.

    :param date: date to be used for the time.
    :param front_matter: the front matter dictionary associated with the file
    :param file_path: the file path of the log file.
    :return datetime object containing the date time start of the file.
    """
    if 'time' in front_matter:
        front_matter_value = front_matter['time']
        return _parse_time_value(date, front_matter_value)
    else:
        print('File: {} doesn\'t have a time value: '.format(file_path))
        return datetime.datetime.combine(date, datetime.time.min)


def get_end_time(start_time, front_matter):
    """
    Parse the end time value out of front matter.  Cannot use a file to determine this value, but the rest of the
    documentation in get_start_time is relevant to this method.
    :param start_time:
    :param front_matter:
    :return:
    """
    if 'end_time' in front_matter and front_matter['end_time']:
        front_matter_value = front_matter['end_time']
        return _parse_time_value(start_time.date(), front_matter_value)
    else:
        return start_time + datetime.timedelta(minutes=DEFAULT_EVENT_LENGTH)


def _parse_time_value(date, time_value):

    if isinstance(time_value, int):
        # Convert it as a duration from midnight of the date.
        return datetime.datetime.combine(date, datetime.time.min) + datetime.timedelta(seconds=time_value)
    elif isinstance(time_value, datetime.datetime):
        return time_value
    else:
        splits = time_value.split(':')
        rv_hours = splits[0]
        rv_minutes = splits[1]
        rv_seconds = 0
        if len(splits) == 3:
            rv_seconds = splits[2]

        return datetime.datetime.combine(date, datetime.time(int(rv_hours), int(rv_minutes), int(rv_seconds)))
