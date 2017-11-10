import requests
import xmltodict


from .day import NanoDay, NanoDaySequence


class NanoBase(object):
    """Base object for pynano API objects.

    This object implements the common functionality for fetching and processing
    API data from the NaNoWriMo API. By default the API is queried "lazily",
    that is requests are only sent when data API is actually requested. This
    behavior can be overridden with the *prefetch* parameter.
    """

    # API name for this object
    _name = None

    # Endpoint URLs for this object; must include a '{name}' placeholder
    _primary_url = None
    _history_url = None

    # The history day class for this object
    _day_class = NanoDay
    # The API field with a given day's date
    _date_field = 'wcdate'

    # Caches for retrieved data
    _data = None
    _history = None

    def __init__(self, name, prefetch=False):
        """
        :param str name: The name of the current object in the NaNoWriMo API
        :param bool prefetch: If True, the API will be queried immediately;
                              otherwise it is queried only when needed
        """

        # Pre-process name before we save it
        name = name.replace(' :: ', '-').replace(' ', '-')
        self._name = name

        if prefetch:
            self._fetch()

    @property
    def history(self):
        """Historical data for this object.

        :rtype: NanoDaySequence
        """
        if self._history is None:
            # Haven't fetched history data yet, do so now
            self._fetch(True)

        # Return the history object
        return self._history

    def _fetch_element(self, index, alt_index=None):
        """Get a particular data element, querying the API if necessary."""
        # We try from alt_index first
        my_index = alt_index or index

        try:
            # Attempt to return the requested data element
            return self._data[my_index]
        except (KeyError, TypeError):
            # Didn't find it, or nothing fetched yet
            if alt_index is not None:
                # Retry without alt_index
                return self._fetch_element(index)
            else:
                # Fetch data from the API
                self._fetch()

            # If we still don't find it, allow the exception to be raised
            return self._data[my_index]

    def _fetch(self, history=False):
        """Fetch data from the API.

        If the history parameter is True, then the history URL will be queried
        for data; if it is False, then the primary URL will be queried.
        """
        if history:
            # Fetching history data
            url = self._history_url
        else:
            # Fetching primary data
            url = self._primary_url

        # Now fetch from the server
        r = requests.get(url.format(name=self._name))
        # Parse the returned data (removing root element)
        data = next(iter(xmltodict.parse(r.text).values()))

        # Now stash the data
        if history:
            # Stash the history data
            self._history = self._process_history(data['wordcounts'])

            if self._data is None:
                # Haven't fetched primary data, stash what we got
                del data['wordcounts']
                self._data = data
        else:
            # Stash the primary data
            self._data = data

    def _process_history(self, history_data):
        """Process the history API's data into an easily-indexed dict."""
        processed = {}

        for data in history_data['wcentry']:
            # Get the date from the proper field
            date = data[self._date_field]

            # Normalize the date field
            del data[self._date_field]
            data['date'] = date

            # Break out the date elements
            year, month, day = date.split('-')

            if month != '11':
                # Do nothing if we somehow got non-November data
                continue

            # Construct a Day object from our data
            the_day = self._day_class(data)
            # Index the data by day less 1 (0-indexed data)
            processed[int(day) - 1] = the_day

        return NanoDaySequence(processed)

