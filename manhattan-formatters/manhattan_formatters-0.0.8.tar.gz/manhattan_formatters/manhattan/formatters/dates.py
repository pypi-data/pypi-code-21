import datetime
import humanize
from inflection import ordinal

__all__ = [
    'humanize_date',
    'humanize_date_range',
    'humanize_datetime',
    'humanize_duration',
    'humanize_time',
    'humanize_timedelta',
    'str_to_date',
    'str_to_datetime',
    'suffix'
    ]


def humanize_date(d):
    """
    Return a humanized a date, e.g: `'3rd September 2016'`. The function accepts
    a date, datetime or date string (YYYY-MM-DD).
    """
    # Convert strings to date instances
    if isinstance(d, str):
        d = str_to_date(d)

    day = '{0}{1}'.format(d.day, suffix(d.day))
    month_year = d.strftime("%B %Y")
    return '{0} {1}'.format(day, month_year)

def humanize_date_range(d1, d2):
    """
    Return a humanized date range, e.g:

    - `'1st - 3rd September 2016'`
    - `'1st August - 3rd September 2016'`
    - `'1st August 2015 - 3rd September 2016'`
    """
    if d1 == d2:
        return humanize_date(d1)

    day1 = '{0}{1}'.format(d1.day, suffix(d1.day))
    day2 = '{0}{1}'.format(d2.day, suffix(d2.day))

    # Days differ
    if d1.year == d2.year and d1.month == d2.month:
        month_year = d1.strftime('%B %Y')
        return '{0} - {1} {2}'.format(day1, day2, month_year)

    # Months differ
    elif d1.year == d2.year:
        month1 = d1.strftime('%B')
        month2_year = d2.strftime('%B %Y')
        return '{0} {1} - {2} {3}'.format(
            day1,
            month1,
            day2,
            month2_year
            )

    # Years differ
    month1_year = d1.strftime('%B %Y')
    month2_year = d2.strftime('%B %Y')
    return '{0} {1} - {2} {3}'.format(
        day1,
        month1_year,
        day2,
        month2_year
        )

def humanize_datetime(dt, template='{date} at {time}'):
    """
    Return a humanized date/time, e.g: `'3rd September 2016, 17:34'`. The
    function accepts a datetime or date/time string (YYYY-MM-DD HH:MM).

    Optionally the default template can be overidden to modify the returned
    string.
    """
    # Convert strings to datetime instances
    if isinstance(dt, str):
        dt = str_to_datetime(dt)

    return template.format(
        date=humanize_date(dt),
        time=humanize_time(dt)
        )

def humanize_duration(m, abbr=True):
    """
    Return a humanized duration for a given number of minutes.

    If `abbr` is True the returned string will be of the form `'2hr 5m'`, if
    `abbr` is False then the returned string will be of the form
    `'2 hours 5 minutes'`.
    """
    minutes_str = 'm' if abbr else ' minutes'
    hours_str = 'hr' if abbr else ' hours'

    if m < 60:
        return "{0}{1}".format(m, minutes_str)
    elif m % 60 == 0:
        return "{0}{1}".format(divmod(m, 60)[0], hours_str)
    else:
        h, m = divmod(m, 60)
        return "{0}{2} {1}{3}".format(h, m, hours_str, minutes_str)

def humanize_time(t):
    """Return a humanized a time (24hr), e.g: `'18:30'`"""
    return t.strftime('%H:%M')

def humanize_timediff(dt):
    """
    Return a humanized time difference between now and the specified datetime,
    e.g:

    - `'a second ago'`
    - `'an hour ago'`
    - `'yesterday'`
    """
    return humanize.naturaltime(dt)

def str_to_date(s):
    """Convert a string (YYYY-MM-DD) to a `datetime.date` instance"""
    return datetime.datetime.strptime(s, '%Y-%m-%d').date()

def str_to_datetime(s):
    """
    Convert a string (YYYY-MM-DD HH:MM:SS) to a `datetime.datetime instance`.
    """
    return datetime.datetime.strptime(s, '%Y-%m-%d %H:%M:%S')

def suffix(i):
    """Return the suffix for a number: e.g: `'st'`, `'nd'`, `'rd'`, `'th'`"""
    return ordinal(i)