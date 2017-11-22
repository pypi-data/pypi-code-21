from ..common import *

NANOSECONDS = 1000000  # nano in milli


class Point(object):
    """
    Point represents a value in the remote API
    """

    def __init__(self, dt, value):
        """
        Representation of a point for a time series

        :param int datetime.datetime datetime.date dt: date for the point
        :param float value: value of the point
        """
        self.date = dt
        self.value = value

    @property
    def value(self):
        """
        Value of the point

        :return: value of the point
        :rtype: float
        """
        return self._val

    @value.setter
    def value(self, value):
        """
        Sets the value of the point, only accepts float

        :param float value: value of the point
        """
        if value is not None:
            value = float(value)  # testing if it's a float
        self._val = value

    @property
    def date(self):
        """
        Date of the point

        :return: date
        :rtype: datetime.date
        """
        return date(self._dt.year, self._dt.month, self._dt.day)

    @date.setter
    def date(self, value):
        """
        Sets the date of the point

        :param int float datetime.datetime datetime.date value:
        :raise ValueError:
        """
        if isinstance(value, six.integer_types + (float,)):
            self._dt = milli_to_datetime(value)
        elif isinstance(value, datetime):
            self._dt = value
        elif isinstance(value, date):
            self._dt = datetime(value.year, value.month, value.day)
        else:
            raise ValueError("You can pass millis or datetime.date objects only")

    @property
    def datetime(self):
        """
        Date of the point as datetime.datetime

        :return: date of the point
        :rtype: datetime.datetime
        """
        return self._dt

    def to_dict(self):
        """
        Returns back a dictionary of the point
        which will be ready to be serialized in the
        next steps ...
        """
        return {
            to_milli(self._dt): self._val
        }

    def __repr__(self):
        return "Point(%s, %s)" % (self._dt, self.value)


def shooju_point(pts):
    return [Point(*p) for p in pts]


def milli_tuple(pts):
    return [(p[0], p[1]) for p in pts]


if PANDAS_INSTALLED:
    def pd_series(pts):
        if not isinstance(pts, numpy.ndarray):
            pts = numpy.array(pts)
        if not len(pts):
            return pandas.Series(index=pandas.DatetimeIndex([]), data=[] )
        return pandas.Series(index=pandas.DatetimeIndex(pts[:, 0] * NANOSECONDS), data=pts[:, 1])

if NUMPY_INSTALLED:
    def np_array(pts):
        if not isinstance(pts, numpy.ndarray):
            return numpy.array(pts)
        else:
            return pts


