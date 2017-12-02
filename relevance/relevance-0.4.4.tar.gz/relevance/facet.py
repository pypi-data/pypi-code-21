"""
This module provides the interface for handling facet definitions. It contains core
facet types, such as term facets and histograms, and the abstract interface for implementing
additional facets.

New facet types should implement the :class:`Facet` interface. When doing so,
:class:`.engine.Engine` implementations will require to be extended with the new functionality
as well.
"""

# pylint: disable=too-few-public-methods

import abc
import typing
import dateutil.parser
from dateutil.relativedelta import relativedelta


class Facet(object):
    """
    The class provides the interface to implement facet types. Sub-classing this class
    is not enough however, each :class:`.engine.Engine` implementation requires to be
    extended to support the new facet type as well.
    """
    def __init__(self, *, field: str = None, path: str = None) -> None:
        """
        :param field: the field for the facet.
        :param path: the path or the facet. Mutually exclusive with `field`. Used when
            a facet is nested.
        :raises: :class:`FacetDefinitionError`: if the facet is defined improperly.
        """
        if field is not None and path is not None:
            raise FacetDefinitionError('field and path are mutually exclusive')

        self.field = field
        self.path = path


class TermFacet(Facet):
    """
    This facet implementation aggregates on facet terms. This is mostly engine specific.
    """
    pass


class HistogramFacet(Facet, metaclass=abc.ABCMeta):
    """
    This interface can implemented to provide new histogram facets, which are typically
    range or interval aggregations.
    """
    @abc.abstractmethod
    def get_range_for(self, value: typing.Any) -> tuple:
        """
        Get a start and end range given a specific value.

        When given an arbitrary value, this method returns the start and end values
        matching the range the value is in.

        :param value: an arbitrary value to get the range for.
        :return: a tuple containing the start and end values for the range.
        """
        pass


class DateFacet(HistogramFacet):
    """
    This facet type aggregates on date and time by using a specific interval.
    """
    YEAR = 'year'
    """ Aggregate by year, with each value being Jan 1st. """

    QUARTER = 'quarter'
    """ Aggregate by quarter, with a value on the first day of Jan, Apr, Jul, Oct. """

    MONTH = 'month'
    """ Aggregate by month, with a value on the first day of each month. """

    WEEK = 'week'
    """ Aggregate by week, with a value each Sunday. """

    DAY = 'day'
    """ Aggregate by day, with a value at midnight on every day. """

    HOUR = 'hour'
    """ Aggregate by hour, with a value at :00:00 every hour. """

    MINUTE = 'minute'
    """ Aggregate by minute. """

    SECOND = 'second'
    """ Aggregate by second. """

    def __init__(self, *, interval: str = MONTH, **kwargs) -> None:
        """
        :param interval: one of the class constants to interval by, \
            e.g.: :const:`DateFacet.YEAR`.
        """
        super().__init__(**kwargs)
        self.interval = interval

    def get_range_for(self, value: typing.Any) -> tuple:  # pylint: disable=too-many-branches
        """
        Implementation of :meth:`HistogramFacet.get_range_for`.

        :raises: :class:`FacetValueError`: if the value is not the start of a range.
        :raises: :class:`FacetDefinitionError`: if an invalid interval has been specified.
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

        props = {'{0}s'.format(prop): delta}
        end = start + relativedelta(**props)  # type: ignore  # pylint: disable=unexpected-keyword-arg

        return start.isoformat(), end.isoformat()


class IntervalFacet(HistogramFacet):
    """
    This facet type aggregates using a specific numeric interval. Per example, if
    `100` is supplied as an interval, ranges of `0..100`, `100..200` will be
    returned. The minimum and maximum ranges depend on the actual data.
    """
    def __init__(self, *, interval: object, **kwargs) -> None:
        """
        :param interval: the numeric interval at which to group the results, typically
            an :class:`int` or a :class:`float`.
        """
        super().__init__(**kwargs)
        self.interval = interval

    def get_range_for(self, value: typing.Union[int, float]) -> tuple:
        """
        Implementation of :meth:`HistogramFacet.get_range_for`.

        :raises: :class:`FacetValueError`: if the value is not the start of a range.
        """
        if (value % self.interval) > 0:  # type: ignore
            raise FacetValueError(self, value)

        return value, value + self.interval  # type: ignore


class RangeFacet(HistogramFacet):
    """
    The facet type aggregates using pre-defined ranges at specific values.
    """
    def __init__(self, *, ranges: dict, **kwargs) -> None:
        """
        :param ranges: a dictionary of ranges with each value being a tuple containing
            a start and an end value. Indefinite values can be specified using `None`.
        """
        super().__init__(**kwargs)
        self.ranges = ranges

    def get_range_for(self, value: object) -> tuple:
        """
        Implementation of :meth:`HistogramFacet.get_range_for`.

        :raises: :class:`FacetValueError`: if the value is not the start of a range.
        """
        try:
            start, end = self.ranges[value]
        except KeyError:
            raise FacetValueError(self, value)

        return start, end


class FacetDefinitionError(TypeError):
    """
    This exception is raised when a facet has not been defined properly. It can be
    because a required option has not been supplied or the supplied value is
    invalid, per example.
    """
    pass


class FacetValueError(ValueError):
    """
    This exception is raised specifically when a requested value is not valid for
    the facet. Per example, if configuring an engine with a :class:`IntervalFacet`
    with a specified interval of `100`, filtering with a value of `50` will raise
    this exception type.
    """
    pass


class FacetNotDefinedError(NameError):
    """
    This exception is raised when a facet is requested but has not yet been
    configured.
    """
    pass


class FacetNotSupportedWarning(UserWarning):
    """
    This warning is raised when an :class:`.engine.Engine` object has been configured
    using a facet type that it does not support.
    """
    def __init__(self, cls: type) -> None:
        """
        :param cls: the facet class that raised the warning.
        """
        super().__init__(cls.__name__)
