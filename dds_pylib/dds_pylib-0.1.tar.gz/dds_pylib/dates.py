"""
Date Functions

History:
08-29-2017 - 1.0.0 - Stephen Funkhouser
    Created
"""
__version__ = "1.0.0"

import datetime


class Gregorian(object):
    """ Gregorian date object

    Note, if the caller changes month/day/year/jd manually the others with be
    automatically calculated to keep these attributes in sync
    """

    def __init__(self, month=0, day=0, year=0, date_str=''):
        """ """
        if date_str:
            date = datetime.datetime.strptime(date_str, '%m-%d-%Y').date()
            self._month = date.month
            self._day = date.day
            self._year = date.year
        else:
            self._month = month
            self._day = day
            self._year = year
        self._jd = None
        self.__calc_julian()

    def __calc_julian(self):
        self._jd = gregorian2julian(m=self._month, d=self._day, y=self._year)

    @property
    def month(self):
        """ property """
        return self._month

    @month.setter
    def month(self, value):
        """ property """
        self._month = value
        # must update jd when month value changes
        self.__calc_julian()

    @month.deleter
    def month(self):
        """ property """
        pass

    @property
    def day(self):
        """ property """
        return self._day

    @day.setter
    def day(self, value):
        """ property """
        self._day = value
        # must update jd when day value changes
        self.__calc_julian()

    @day.deleter
    def day(self):
        """ property """
        pass

    @property
    def year(self):
        """ property """
        return self._year

    @year.setter
    def year(self, value):
        """ property """
        self._year = value
        # must update jd when year value changes
        self.__calc_julian()

    @year.deleter
    def year(self):
        """ property """
        pass

    @property
    def jd(self):
        """ property """
        return self._jd

    @jd.setter
    def jd(self, value):
        """ property """
        self._jd = value
        # must update month,day,year when jd changes
        gregorian = julian2gregorian(julian=self._jd, todays_jd=False)
        self._month = gregorian.month
        self._day = gregorian.day
        self._year = gregorian.year

    @jd.deleter
    def jd(self):
        """ property """
        pass

    def tuple(self):
        """ return (m, d, y) tuple """
        return (self._month, self._day, self._year,)

    def julian(self):
        """ return equivalent julian _day """
        return self._jd

    def pydate(self):
        """ return date object """
        return datetime.date(year=self._year, month=self._month, day=self._day)

    def pydatetime(self):
        """ return datetime object """
        return datetime.datetime(year=self._year, month=self._month, day=self._day)

    def strdate(self):
        """ return date string. Currently US format
        """
        return '{m}-{d}-{y}'.format(m=self._month, d=self._day, y=self._year)

    def __eq__(self, obj):
        return isinstance(obj, Gregorian) and obj._jd == self._jd

    def __str__(self):
        return '{m}-{d}-{y} : jd={jd}'.format(m=self._month, d=self._day, y=self._year, jd=self._jd)


def todays_julian():
    """ get today's julian _day """
    dnow = datetime.datetime.now()
    return gregorian2julian(m=dnow.month, d=dnow.day, y=dnow.year)


def gregorian2julian(m=0, d=0, y=0):
    """ convert gregorian m/d/y to jualian _day """
    #=========================================================================
    # Fliegel-Van Flandern algorithm
    #=========================================================================
    temp1 = m - 14
    temp2 = d - 32075 + 1461 * (y + 4800 + int(temp1 / 12.0)) / 4
    temp3 = int(temp1 / 12.0) * 12
    temp4 = ((y + 4900 + int(temp1 / 12.0)) / 100)
    jd = temp2 + 367 * (m - 2 - temp3) / 12 - 3 * temp4 / 4
    return jd


def julian2gregorian(julian=0, todays_jd=False):
    """ convert julian _day to gregorian m/d/y

    params:
        julian    -
        todays_jd - True/False

    returns:
        Gregorian instance
    """
    julian = int(julian)
    if julian <= 0 and todays_jd:
        julian = todays_julian()
    elif julian <= 0 and not todays_jd:
        raise Exception(
            'You must specify either a julian _day or allow today\'s julian to be used')
    #=========================================================================
    # Fliegel-Van Flandern algorithm
    #=========================================================================
    p = int(julian + 68569)
    q = int(4 * p / 146097)
    r = int(p - (146097 * q + 3) / 4)
    s = int(4000 * (r + 1) / 1461001)
    t = int(r - 1461 * s / 4 + 31)
    u = int(80 * t / 2447)
    v = int(u / 11)

    Y = int(100 * (q - 49) + s + v)
    M = int(u + 2 - 12 * v)
    D = int(t - 2447 * u / 80)
    return Gregorian(month=M, day=D, year=Y)
