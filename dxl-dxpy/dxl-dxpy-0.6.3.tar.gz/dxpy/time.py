# Author: Hong Xiang <hx.hongxiang@gmail.com>

"""
A time utility module, used for measure, record and analysis of time related tasks, all time in float are defined in
millisecond, this module defines the following classes:

- `TimeStamp`, a time stamp

Exception classes:

Functions:


"""

import json
import yaml
import datetime
import re
from dxpy.utils import Tags


def _parse_time_delta(s):
    if s is None:
        return None
    d = re.match(
        r'((?P<days>\d+) days?, )?(?P<hours>\d+):' +
        r'(?P<minutes>\d+):(?P<seconds>\d+)(\.(?P<microseconds>\d+))?',
        str(s)).groupdict(0)
    return datetime.timedelta(**dict(((key, int(value))
                                      for key, value in d.items())))


def now():
    return datetime.datetime.now()

class TimeStamps:
    """ A dict of time stamps
    """
    def __init__(self, time_stamps=None):
        if not isinstance(time_stamps, dict):
            raise TypeError("time_stamps must be a dict, not {}.".format(type(time_stamps)))
        for k in time_stamps:
            if not isinstance()
        self.time_stamps = time_stamps   


class TimeStamp(yaml.YAMLObject):
    """ A time stamp object.


    Members:

    - start: float, start time in secs,
    - run: float, run time in secs,
    - end: float, [Optional, Default=0.0], end time in secs

    Methods:


    """

    yaml_tag = '!time_stamp'

    DATETIMEFORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(self, start=None, run=None, end=None):
        self.start = start or now()
        self.run = run or now() - self.start
        self.end = end

    def now(self):
        return TimeStamp(self.start, end=self.end)

    @property
    def eta(self):
        if self.end > self.start:
            eta_now = self.end - self.start - self.run
            if eta_now < datetime.timedelta(0.0):
                return datetime.timedelta(0.0)
            else:
                return eta_now
        else:
            return None

    @classmethod
    def format_datetime(cls, dt):
        if dt is None:
            return Tags.undifined
        else:
            return datetime.datetime.strftime(dt, TimeStamp.DATETIMEFORMAT)

    @classmethod
    def format_duration(cls, td):
        return str(td)

    @classmethod
    def parse_datetime(cls, dt):
        if dt == Tags.undifined:
            return None
        return datetime.datetime.strptime(dt, TimeStamp.DATETIMEFORMAT)

    @classmethod
    def parse_duration(cls, td):
        return _parse_time_delta(td)

    @classmethod
    def to_yaml(cls, dumper, data):
        return yaml.MappingNode(cls.yaml_tag, value=[
            (yaml.ScalarNode(tag='tag:yaml.org,2002:str', value='start'),
             yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=TimeStamp.format_datetime(data.start))),
            (yaml.ScalarNode(tag='tag:yaml.org,2002:str', value='run'),
             yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=TimeStamp.format_duration(data.run))),
            (yaml.ScalarNode(tag='tag:yaml.org,2002:str', value='end'),
             yaml.ScalarNode(tag='tag:yaml.org,2002:str', value=TimeStamp.format_datetime(data.end)))
        ])

    @classmethod
    def from_yaml(cls, loader, node):
        data = loader.construct_mapping(node)
        start = TimeStamp.parse_datetime(data['start'])
        end = TimeStamp.parse_datetime(data['end'])
        run = TimeStamp.parse_duration(data['run'])
        return TimeStamp(start, run, end)


def estimate_end(ts, ratio):
    time_ela = ts.run
    time_total = time_ela / ratio
    time_end = ts.start + time_total
    return TimeStamp(ts.start, end=time_end)
