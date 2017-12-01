from datetime import datetime

import pytz

from dateutil.rrule import rrule, DAILY, HOURLY, MONTHLY, YEARLY
from dateutil.parser import parse as capture
from dateutil.tz import tzlocal
from dateutil.tz import tzoffset
from tzlocal import get_localzone

from .exceptions import TardisInvalidDatetime
from .dates import Tardis, is_datetime_naive, datetime_timezone


def parse(datetime_str, timezone=None, dayfirst=True, yearfirst=True):
    """
    Parses a datetime string and returns a `Tardis` object.

    :param datetime_str: The string to be interpreted into a `Tardis` object.
    :param timezone: Pass this parameter and the returned Tardis object will be normalized to this timezone. Any
        offsets passed as part of datetime_str will be ignored.
    :param dayfirst: Whether to interpret the first value in an ambiguous 3-integer date (ex. 01/05/09) as the day
        (True) or month (False). If yearfirst is set to True, this distinguishes between YDM and YMD.
    :param yearfirst: Whether to interpret the first value in an ambiguous 3-integer date (ex. 01/05/09) as the
        year. If True, the first number is taken to be the year, otherwise the last number is taken to be the year.

    .. testsetup::

        from tardis import Tardis
        from tardis import parse

    .. doctest::

        >>> parse('2015-01-01 00:01:02')
        Tardis(datetime=datetime.datetime(2015, 1, 1, 0, 1, 2), timezone='UTC')

    If a fixed offset is provided in the datetime_str, it will be parsed and the returned `Tardis` object will store a
    `pytz.FixedOffest` as it's timezone.

    .. doctest::

        >>> parse('2015-01-01 00:01:02 -0800')
        Tardis(datetime=datetime.datetime(2015, 1, 1, 0, 1, 2), timezone=pytz.FixedOffset(-480))

    If the timezone argument is supplied, the returned Tardis object will be in the timezone supplied. Any offsets in
    the datetime_str will be ignored.

    .. doctest::

        >>> parse('2015-01-01 00:01:02 -0500', timezone='US/Pacific')
        Tardis(datetime=datetime.datetime(2015, 1, 1, 0, 1, 2), timezone='US/Pacific')

    If an unambiguous timezone is detected in the datetime string, a Tardis object with that datetime and
    timezone will be returned.

    .. doctest::

        >>> parse('2015-01-01 00:01:02 PST')
        Tardis(datetime=datetime.datetime(2015, 1, 1, 0, 1, 2), timezone='America/Los_Angeles')

    However if the provided timezone is ambiguous, parse will ignore the timezone and return a `Tardis` object in UTC
    time.

        >>> parse('2015-01-01 00:01:02 EST')
        Tardis(datetime=datetime.datetime(2015, 1, 1, 0, 1, 2), timezone='UTC')

    """
    dt = capture(datetime_str, dayfirst=dayfirst, yearfirst=yearfirst)

    if timezone:
        dt = dt.replace(tzinfo=None)
        do = Tardis(datetime=dt, timezone=timezone)
    elif dt.tzinfo is None:
        # assuming datetime object passed in is UTC
        do = Tardis(datetime=dt, timezone='UTC')
    elif isinstance(dt.tzinfo, tzoffset):
        utcoffset = dt.tzinfo.utcoffset(None)
        total_seconds = (
            (utcoffset.microseconds + (utcoffset.seconds + utcoffset.days * 24 * 3600) * 10**6) / 10**6)

        tz = pytz.FixedOffset(total_seconds / 60)
        dt = dt.replace(tzinfo=None)
        do = Tardis(dt, timezone=tz)
    elif isinstance(dt.tzinfo, tzlocal):
        tz = get_localzone()
        dt = dt.replace(tzinfo=None)
        do = Tardis(dt, timezone=tz)
    else:
        dt = pytz.utc.normalize(dt)
        # making dt naive so we can pass it to Tardis
        dt = dt.replace(tzinfo=None)
        # if parse string has tzinfo we return a normalized UTC
        # tardis object that represents the time.
        do = Tardis(datetime=dt, timezone='UTC')

    return do


def range_daily(start=None, stop=None, timezone='UTC', count=None):
    """
    This an alternative way to generating sets of Tardis objects with
    DAILY stops
    """
    return stops(start=start, stop=stop, freq=DAILY, timezone=timezone, count=count)


def range_hourly(start=None, stop=None, timezone='UTC', count=None):
    """
    This an alternative way to generating sets of Tardis objects with
    HOURLY stops
    """
    return stops(start=start, stop=stop, freq=HOURLY, timezone=timezone, count=count)


def range_monthly(start=None, stop=None, timezone='UTC', count=None):
    """
    This an alternative way to generating sets of Tardis objects with
    MONTHLY stops
    """
    return stops(start=start, stop=stop, freq=MONTHLY, timezone=timezone, count=count)


def range_yearly(start=None, stop=None, timezone='UTC', count=None):
    """
    This an alternative way to generating sets of Tardis objects with
    YEARLY stops
    """
    return stops(start=start, stop=stop, freq=YEARLY, timezone=timezone, count=count)


def stops(freq, interval=1, count=None, wkst=None, bysetpos=None,
          bymonth=None, bymonthday=None, byyearday=None, byeaster=None,
          byweekno=None, byweekday=None, byhour=None, byminute=None,
          bysecond=None, timezone='UTC', start=None, stop=None):
    """
    This will create a list of tardis objects the apply to
    setting possed in.
    """
    # check to see if datetimees passed in are naive if so process them
    # with given timezone.
    if all([(start is None or is_datetime_naive(start)),
            (stop is None or is_datetime_naive(stop))]):
        pass
    else:
        raise TardisInvalidDatetime('Provide a naive datetime object')

    # if no datetimes are passed in create a proper datetime object for
    # start default because default in dateutil is datetime.now() :(
    if start is None:
        start = datetime_timezone(timezone)

    for dt in rrule(freq, interval=interval, count=count, wkst=wkst, bysetpos=bysetpos,
          bymonth=bymonth, bymonthday=bymonthday, byyearday=byyearday, byeaster=byeaster,
          byweekno=byweekno, byweekday=byweekday, byhour=byhour, byminute=byminute,
          bysecond=bysecond, until=stop, dtstart=start):
        # make the tardis object
        # yield it.
        # doing this to make sure tardis receives a naive datetime.
        dt = dt.replace(tzinfo=None)
        d = Tardis(datetime=dt, timezone=timezone)
        yield d


def epoch(s):
    dt = datetime.utcfromtimestamp(s)
    return Tardis(datetime=dt, timezone='UTC')


def flux():
    print("If you put your mind to it, you can accomplish anything.")


def utcnow():
    """
    Return a Tardis object for the current UTC date and time, setting the timezone to UTC.
    """
    return Tardis()


def now():
    """
    Return a Tardis object for the current local date and time, setting the timezone to the local timezone of the
    caller.
    """
    return Tardis(timezone=get_localzone())
