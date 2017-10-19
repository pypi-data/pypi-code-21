"""TimeSpan"""
# Author: Michal Ciesielczyk
# Licence: MIT
import datetime


class TimeSpan(datetime.timedelta):
    """Represents a time span.

    All arguments are optional and default to 0. Arguments may be integers or
    floats, and may be positive or negative.

    As in the base :py:class:`python:datetime.timedelta` class, only days,
    seconds and microseconds are stored internally. Arguments are converted to
    those units:

        - A millisecond is converted to 1000 microseconds.
        - A minute is converted to 60 seconds.
        - An hour is converted to 3600 seconds.

    and days, seconds and microseconds are then normalized so that the
    representation is unique.

    If any argument is a float and there are fractional microseconds, the
    fractional microseconds left over from all arguments are combined and their
    sum is rounded to the nearest microsecond using round-half-to-even
    tiebreaker.

    :param float,optional seconds: number of seconds in the time span.
    :param float,optional microseconds: number of microseconds in the time span.
    :param float,optional milliseconds: number of milliseconds in the time span.
    :param float,optional minutes: number of minutes in the time span.
    :param float,optional hours: number of hours in the time span.
    :param float,optional days: number of days in the time span.
    """

    def __new__(cls, seconds=0, microseconds=0, milliseconds=0,
                minutes=0, hours=0, days=0):
        return datetime.timedelta.__new__(cls, days=days, seconds=seconds,
                                          microseconds=microseconds,
                                          milliseconds=milliseconds,
                                          minutes=minutes, hours=hours)

    def total_hours(self):
        """Total hours in the duration."""
        return (self.days * 24 + self.seconds / 3600 +
                self.microseconds / 3600000000)

    def total_minutes(self):
        """Total minutes in the duration."""
        return (self.days * 1440 + self.seconds / 60 +
                self.microseconds / 60000000)

    def total_milliseconds(self):
        """Total milliseconds in the duration."""
        return (self.days * 86400000 + self.seconds * 1000 +
                self.microseconds / 1000)

    def human_str(self, trim_zeros=True, significant_digits=None):
        """Returns a human-readable string representation of the
        :py:class:`~.timespan.TimeSpan` object, using time units such as days,
        hours, minutes, and seconds.

        :param bool,optional trim_zeros: indicates whether the leading zeros
            in the result should be skipped
        :param int,optional significant_digits: if set, returns a string
            representation of a single number with an appropriate time unit and
            using the specified number of significant figures
        :return: human-readable time span
        :rtype: str

        .. versionadded:: 0.3.1
            The *significant_digits* parameter.
        """
        if significant_digits is not None:
            hstr = "{val:.{p}f} {unit}"
            if self.days > 0:
                return hstr.format(val=self.total_hours() / 24,
                                   p=significant_digits, unit="days")
            elif self.total_hours() > 1:
                return hstr.format(val=self.total_hours(),
                                   p=significant_digits, unit="hours")
            elif self.total_minutes() > 1:
                return hstr.format(val=self.total_minutes(),
                                   p=significant_digits, unit="minutes")
            elif self.total_seconds() > 1:
                return hstr.format(val=self.total_seconds(),
                                   p=significant_digits, unit="seconds")
            return hstr.format(val=self.total_milliseconds(),
                               p=significant_digits, unit="milliseconds")
        if self.total_seconds() < 1:
            return "{:d} ms".format(self.microseconds // 1000)
        human = []
        if self.days > 0 or not trim_zeros:
            name = "day" if self.days == 1 else "days"
            human.append("{:d} {:s}".format(self.days, name))
        units = [("hours", 3600), ("mins", 60), ("secs", 1)]
        seconds_left = self.seconds
        for name, secs in units:
            if trim_zeros and self.seconds < secs:
                continue
            value = seconds_left // secs
            seconds_left %= secs
            if value == 1:
                name = name.rstrip('s')
            human.append("{:d} {:s}".format(value, name))
        return ', '.join(human)
