import datetime

from freezegun import freeze_time

from manhattan import formatters


def test_humanize_date():
    """Return a human readable formatted date"""

    # Check that date and datetime instances are supported
    dt = datetime.datetime(2016, 1, 1)
    assert formatters.dates.humanize_date(dt.date()) == '1st January 2016'
    assert formatters.dates.humanize_date(dt) == '1st January 2016'

    # Check that a date string in the format YYYY-MM-DD is supported
    assert formatters.dates.humanize_date('2016-01-01') == '1st January 2016'

def test_humanize_date_range():
    """Return a human readable date range"""

    # Check format of 2 identical dates
    d = datetime.date(2016, 1, 1)
    assert formatters.dates.humanize_date_range(d, d) == '1st January 2016'

    # Check format of 2 in the same month
    d1 = datetime.date(2016, 1, 1)
    d2 = datetime.date(2016, 1, 15)
    assert formatters.dates.humanize_date_range(d1, d2) == '1st - 15th January 2016'

    # Check format of 2 dates in different months
    d1 = datetime.date(2016, 1, 1)
    d2 = datetime.date(2016, 8, 1)
    assert formatters.dates.humanize_date_range(d1, d2) == '1st January - 1st August 2016'

    # Check format of 2 dates in different years
    d1 = datetime.date(2016, 1, 1)
    d2 = datetime.date(2018, 1, 1)
    assert formatters.dates.humanize_date_range(d1, d2) == \
            '1st January 2016 - 1st January 2018'

    # Check format of 2 dates in different years where the first date is after
    # the second.
    d1 = datetime.date(2017, 1, 1)
    d2 = datetime.date(2016, 1, 1)
    assert formatters.dates.humanize_date_range(d1, d2) == \
            '1st January 2017 - 1st January 2016'

def test_humanize_datetime():
    """Return a human readable date/time"""

    # Check datetime is supported
    dt = datetime.datetime(2016, 1, 1, 9, 15)
    assert formatters.dates.humanize_datetime(dt) == '1st January 2016 at 09:15'

    # Check a date/time string in the format YYYY-MM-DD HH:MM:SS is supported
    assert formatters.dates.humanize_datetime('2016-01-01 09:15:30') == \
            '1st January 2016 at 09:15'

    # Check format is correct for a custom template
    assert formatters.dates.humanize_datetime(dt, '{time} on {date}') == \
            '09:15 on 1st January 2016'

def test_humanize_duration():
    """Return a human readable duration for a given number of minutes"""

    # Check format for less than 60 minutes (minutes only)
    assert formatters.dates.humanize_duration(5) == '5m'
    assert formatters.dates.humanize_duration(5, abbr=False) == '5 minutes'

    # Check format for multiple of 60 (hours only)
    assert formatters.dates.humanize_duration(120) == '2hr'
    assert formatters.dates.humanize_duration(120, abbr=False) == '2 hours'

    # Check format for non multiple greater than 60 (hours and minutes)
    assert formatters.dates.humanize_duration(150) == '2hr 30m'
    assert formatters.dates.humanize_duration(150, abbr=False) == '2 hours 30 minutes'

def test_humanize_time():
    """Return a human readable time"""

    # Check datetime and time are supported
    dt = datetime.datetime(2017, 1, 1, 9, 15)
    assert formatters.dates.humanize_time(dt) == '09:15'
    assert formatters.dates.humanize_time(dt.time()) == '09:15'

@freeze_time('2016-09-01 09:15:00')
def humanize_timediff():
    """
    Return a humanized time difference between now and the specified datetime.
    """

    # Check 5 minutes from now
    d = datetime.datetime(2016, 9, 1, 9, 20)
    assert formatters.dates.humanize_timedelta(d) == '5 minutes from now'

    # Check 3 months from now
    d = datetime.datetime(2016, 12, 30, 9, 15)
    assert formatters.dates.humanize_timedelta(d) == '3 months from now'

    # Check 2 years from now
    d = datetime.datetime(2018, 9, 1, 9, 15)
    assert formatters.dates.humanize_timedelta(d) == '2 years from now'

    # Check 5 minutes ago
    d = datetime.datetime(2016, 9, 1, 9, 10)
    assert formatters.dates.humanize_timedelta(d) == '5 minutes ago'

    # Check 3 months ago
    d = datetime.datetime(2016, 6, 1, 9, 15)
    assert formatters.dates.humanize_timedelta(d) == '3 months ago'

    # Check 2 years ago
    d = datetime.datetime(2014, 9, 1, 9, 15)
    assert formatters.dates.humanize_timedelta(d) == '2 years ago'

def test_str_to_date():
    """Convert a string (YYYY-MM-DD) to a `datetime.date` instance"""

    # Check a `datetime.date` instance of the correct date is returned
    d = formatters.dates.str_to_date('2016-06-15')
    assert isinstance(d, datetime.date)
    assert d == datetime.date(2016, 6, 15)

def test_str_to_datetime():
    """
    Convert a string (YYYY-MM-DD HH:MM:SS) to a `datetime.datetime instance`.
    """

    # Check a `datetime.datetime` instance of the correct date is returned
    d = formatters.dates.str_to_datetime('2016-06-15 09:15:30')
    assert isinstance(d, datetime.datetime)
    assert d == datetime.datetime(2016, 6, 15, 9, 15, 30)

def test_suffix():
    """Return the suffix for a number, e.g. st, nd, rd"""
    assert formatters.dates.suffix(1) == 'st'
    assert formatters.dates.suffix(2) == 'nd'
    assert formatters.dates.suffix(3) == 'rd'
    assert formatters.dates.suffix(4) == 'th'