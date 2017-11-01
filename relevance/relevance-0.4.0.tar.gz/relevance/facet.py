"""
Relevance facets module.

This module provides the interface definitions for handling facets.
"""

import abc
import dateutil.parser
from dateutil.relativedelta import relativedelta


class FacetDefinitionError(TypeError):
    """
    Exception class raised when a facet is not defined properly.
    """
    pass


class FacetValueError(ValueError):
    """
    Exception class raised when a requested facet value is invalid.
    """
    def __init__(self, value: str):
        """
        Initialize the exception.

        :param value: the value of the facet that caused the error.
        """
        super().__init__('invalid facet value {0}'.format(value))
        self.value = value


class FacetNotDefinedError(NameError):
    """
    Exception class raised when a requested facet is not defined.
    """
    def __init__(self, name: str):
        """
        Initialize the exception.

        :param name: the name of the facet that caused the error.
        """
        super().__init__('the facet {0} is not defined'.format(name))
        self.name = name


class FacetNotSupportedWarning(UserWarning):
    """
    Warning class when an engine does not support a specifi facet.
    """
    def __init__(self, cls: type):
        """
        Initialize the exception.

        :param cls: the facet class that raised the warning.
        """
        super().__init__('the facet type {0} is not supported by the engine'.format(
            cls.__name__
        ))
        self.cls = cls


class Facet(object):
    """
    Base facet definition class.
    """
    def __init__(self, *, field: str=None, path: str=None):
        """
        Initialize the definition.

        :param field: the field for the facet.
        :param path: the path or the facet. Mutually exclusive with field. Used when
        a facet is nested.
        :raises FacetDefinitionError: if the facet is defined improperly.
        """
        if field is not None and path is not None:
            raise FacetDefinitionError('field and path are mutually exclusive')

        self.field = field
        self.path = path


class TermFacet(Facet):
    """
    Facet type for term facets.

    Aggregates on matching terms.
    """
    pass


class HistogramFacet(Facet, metaclass=abc.ABCMeta):
    """
    Facet type for histogram facets.

    Facets that use ranges should inherit from this abstract class.
    """
    @abc.abstractmethod
    def get_range_for(self, value: object) -> tuple:
        """
        Get a start and end range given a specific value.

        :param value: the value to get the range for.
        :returns: a tuple containing the start and end values for the range.
        """
        pass


class DateFacet(HistogramFacet):
    """
    Facet type for date/time histogram facets.

    Aggregates on date intervals.
    """
    # Interval definitions
    YEAR = 'year'
    QUARTER = 'quarter'
    MONTH = 'month'
    WEEK = 'week'
    DAY = 'day'
    HOUR = 'hour'
    MINUTE = 'minute'
    SECOND = 'second'

    def __init__(self, *, interval: str=MONTH, **kwargs):
        """
        Initialize the facet.

        :param interval: the interval at which to group the results.
        """
        super().__init__(**kwargs)
        self.interval = interval

    def get_range_for(self, value: object) -> tuple:
        """
        Override abstract method.

        :raises FacetValueError: if an invalid range is specified.
        :raises FacetDefinitionError: if the facet is defined improperly.
        """
        start = dateutil.parser.parse(value)
        prop, delta = self.interval, 1

        if self.interval == DateFacet.YEAR:
            if start.month != 1 or start.day != 1 or start.hour != 0 or \
               start.minute != 0 or start.second != 0:
                raise FacetValueError(value)

        elif self.interval == DateFacet.QUARTER:
            if start.month not in [1, 4, 7, 10] or start.day != 1 or \
               start.hour != 0 or start.minute != 0 or start.second != 0:
                raise FacetValueError(value)
            prop, delta = 'month', 3

        elif self.interval == DateFacet.MONTH:
            if start.day != 1 or start.hour != 0 or \
               start.minute != 0 or start.second != 0:
                raise FacetValueError(value)

        elif self.interval == DateFacet.WEEK:
            if start.weekday() != 0:
                raise FacetValueError(value)
            prop, delta = 'day', 7

        elif self.interval == DateFacet.DAY:
            if start.hour != 0 or start.minute != 0 or start.second != 0:
                raise FacetValueError(value)

        elif self.interval == DateFacet.HOUR:
            if start.minute != 0 or start.second != 0:
                raise FacetValueError(value)

        elif self.interval == DateFacet.MINUTE:
            if start.second != 0:
                raise FacetValueError(value)

        else:
            raise FacetDefinitionError('invalid interval {0}'.format(self.interval))

        end = start + relativedelta(**{'{0}s'.format(prop): delta})

        return start.isoformat(), end.isoformat()


class IntervalFacet(HistogramFacet):
    """
    Facet type for numeric interval facets.

    Aggregates on numeric intervals.
    """
    def __init__(self, *, interval: object, **kwargs):
        """
        Initialize the facet.

        :param interval: the interval at which to group the results.
        """
        super().__init__(**kwargs)
        self.interval = interval

    def get_range_for(self, value: object) -> tuple:
        """
        Override abstract method.

        :raises FacetValueError: if an invalid range is specified.
        """
        if (value % self.interval) > 0:
            raise FacetValueError(self, value)

        return value, value + self.interval


class RangeFacet(HistogramFacet):
    """
    Facet type for rangeed histogram facets.

    Aggregates on specific numeric intervals.
    """
    def __init__(self, *, ranges: dict, **kwargs):
        """
        Initialize the facet.

        :param ranges: a dictionary of ranges with each value being a tuple containing
        a start and an end value.
        """
        super().__init__(**kwargs)
        self.ranges = ranges

    def get_range_for(self, value: object) -> tuple:
        """
        Override abstract method.

        :raises FacetValueError: if an invalid range is specified.
        """
        try:
            start, end = self.ranges[value]
        except KeyError:
            raise FacetValueError(self, value)

        return start, end
