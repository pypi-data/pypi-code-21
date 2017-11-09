from decimal import Decimal


from .base import NanoBase
from .day import NanoDay


class RegionDay(NanoDay):
    """A Day in the history of a region.

    .. note::
       The API does not provide daily word counts for regions, and due to
       the `average` seemingly being based on who posted updates rather than on
       `count`, it cannot at this time be calculated.
    """
    @property
    def wordcount(self):
        """The API doesn't provide daily word counts for regions.

        :raises AttributeError: on all calls due to it not being in the API.
        """
        raise AttributeError("'RegionDay' object has no attribute 'wordcount'")

    @property
    def min(self):
        """Minimum word count posted to the region this day.

        Corresponds to `min` in the API.

        :rtype: int
        """
        return int(self._data['min'])

    @property
    def max(self):
        """Maximum word count posted to the region this day.

        Corresponds to `max` in the API.

        :rtype: int
        """
        return int(self._data['max'])

    @property
    def average(self):
        """Average word count posted to the region this day.

        Corresponds to `average` in the API.

        :rtype: Decimal
        """
        return Decimal(self._data['average'])

    @property
    def stddev(self):
        """Standard deviation of word counts posted to the region this day.

        Corresponds to `stddev` in the API.

        :rtype: Decimal
        """
        return Decimal(self._data['stddev'])

    @property
    def writers(self):
        """Writers in the region.

        Corresponds to `count` in the API.

        :rtype: int
        """
        return int(self._data['count'])

    @property
    def donations(self):
        """Donations made from this region on this day.

        Corresponds to `donations` in the API.

        :rtype: Decimal
        """
        return Decimal(self._data['donations'] or '0.0')

    @property
    def donors(self):
        """Number of people donating from this region on this day.

        Corresponds to `numdonors` in the API.

        :rtype: int
        """
        return int(self._data['numdonors'] or 0)


class Region(NanoBase):
    """A NanoBase object to represent NaNoWriMo regions from the API."""
    # Endpoint URLs for region objects
    _primary_url = 'http://nanowrimo.org/wordcount_api/wcregion/{name}'
    _history_url = 'http://nanowrimo.org/wordcount_api/wcregionhist/{name}'

    # Use our own Day object
    _day_class = RegionDay
    # The day field for the history API
    _date_field = 'date'

    @property
    def id(self):
        """Region ID.

        Corresponds to `rid` in the API.

        :rtype: string
        """
        return self._fetch_element('rid')

    @property
    def name(self):
        """Region name.

        Corresponds to `rname` in the API.

        :rtype: string
        """
        return self._fetch_element('rname')

    @property
    def wordcount(self):
        """Region word count.

        Corresponds to `word count` in the API.

        :rtype: int
        """
        return int(self._fetch_element('region_wordcount'))

    @property
    def min(self):
        """Minimum word count in the region.

        Corresponds to `min` in the API.

        :rtype: int
        """
        return int(self._fetch_element('min'))

    @property
    def max(self):
        """Maximum word count in the region.

        Corresponds to `max` in the API.

        :rtype: int
        """
        return int(self._fetch_element('max'))

    @property
    def average(self):
        """Average word count in the region.

        Corresponds to `average` in the API.

        :rtype: Decimal
        """
        return Decimal(self._fetch_element('average'))

    @property
    def stddev(self):
        """Standard deviation of word counts in the region.

        Corresponds to `stddev` in the API.

        :rtype: Decimal
        """
        return Decimal(self._fetch_element('stddev'))

    @property
    def writers(self):
        """Writers in the region.

        Corresponds to `count` in the API.

        :rtype: int
        """
        return int(self._fetch_element('count', alt_index='numparticipants'))

    @property
    def donations(self):
        """Donations made from the region.

        Corresponds to `donations` in the API.

        :rtype: Decimal
        """
        return Decimal(self._fetch_element('donations'))

    @property
    def donors(self):
        """Donors from the region.

        Corresponds to `numdonors` in the API.

        :rtype: int
        """
        return int(self._fetch_element('numdonors'))

