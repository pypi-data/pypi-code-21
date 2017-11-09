import sys
from decimal import Decimal


from .base import NanoBase
from .day import NanoDay


if sys.version_info < (3, 0, 0):
    # We're on Py2, get Py3-style super()
    from builtins import super


class SiteDay(NanoDay):
    """A Day in the history of the site.
    """
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
        """Average of word counts posted to the region this day.

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
    def count(self):
        """Corresponds to `count` in the API

        .. todo::
           Figure out what this one actually is.

        :rtype: int
        """
        return int(self._data['count'])


class Site(NanoBase):
    # Endpoint URLs for region objects
    _primary_url = 'http://nanowrimo.org/wordcount_api/wcstatssummary{name}'
    _history_url = 'http://nanowrimo.org/wordcount_api/wcstats{name}'

    # Use our own Day object
    _day_class = SiteDay

    def __init__(self, *args, **kwargs):
        """
        :param bool prefetch: If True, the API will be queried immediately;
                              otherwise it is queried only when needed

        .. note::
           Site objects, unlike other NaNoWriMo API objects, do not have a name
           attribute. We override the __init__() method to remove the name
           parameter and supply an empty string to the parent's method.
        """
        super().__init__(name='', *args, **kwargs)

    @property
    def wordcount(self):
        """Word count for the site.

        Corresponds to `site_wordcount` in the API.

        :rtype: int
        """
        # History API has alternative names for some reason, try those too
        wordcount = self._fetch_element('site_wordcount',
                                        alt_index='site_word_count')

        return int(wordcount)

    @property
    def min(self):
        """Minimum word count for the site.

        Corresponds to `min` in the API.

        :rtype: int
        """
        return int(self._fetch_element('min'))

    @property
    def max(self):
        """Maximum word count for the site.

        Corresponds to `max` in the API.

        :rtype: int
        """
        return int(self._fetch_element('max'))

    @property
    def average(self):
        """Average word count for the site.

        Corresponds to `average` in the API.

        :rtype: Decimal
        """
        return Decimal(self._fetch_element('average'))

    @property
    def stddev(self):
        """Standard deviation of word counts for the site.

        Corresponds to `stddev` in the API.

        :rtype: Decimal
        """
        return Decimal(self._fetch_element('stddev'))

    @property
    def writers(self):
        """Number of writers participating on the site.

        Corresponds to `count` in the API.

        :rtype: int
        """
        # History API has alternative names for some reason, try those too
        writers = self._fetch_element('count', alt_index='numparticipants')

        return int(writers)

