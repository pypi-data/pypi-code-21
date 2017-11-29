# coding: utf-8
"""
Equality test utilities.
"""
import datetime

class AnyBase(object):
    """
    Base class.
    """
    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return '<{}>'.format(type(self).__name__)


class AnyInt(AnyBase):
    """
    Compares equal to any integer.
    """
    def __eq__(self, other):
        return isinstance(other, int)


class AnyTimestamp(AnyBase):
    """
    Compares equal to a string timestamp that is within a given number of
    seconds from a given datetime.

    Currently assumes string timestamp format is yyyy-mm-ddThh:mm:ss-hh:mm.
    Currently strips and ignores the '-hh:mm' timezone suffix.
    """
    def __init__(self, baseline, seconds=10):
        """
        baseline: A datetime to compare against.
        seconds: A number of seconds.
        """
        self.baseline = baseline
        self.seconds = seconds

    def __eq__(self, other):
        # strip tz info if present, we don't currently use it.
        if len(other) == 25 and other[-6] in '+-':
            other = other[:19]
        other_dt = datetime.datetime.strptime(other, "%Y-%m-%dT%H:%M:%S")
        difference = (self.baseline - other_dt).total_seconds()
        return abs(difference) <= self.seconds

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return u'<AnyTimestamp {} +/- {} secs>'.format(
            self.baseline.isoformat(), self.seconds
        )

