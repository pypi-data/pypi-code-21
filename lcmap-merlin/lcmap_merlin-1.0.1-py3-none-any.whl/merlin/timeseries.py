from collections import Counter
from cytoolz import do
from cytoolz import excepts
from cytoolz import first
from cytoolz import identity
from cytoolz import juxt
from cytoolz import partial
from cytoolz import pipe
from cytoolz import reduce
from cytoolz import second
from cytoolz import thread_first
from datetime import datetime
from merlin import chips
from merlin import chip_specs as specs
from merlin import dates as mdates
from merlin import functions as f
from merlin import rods as mrods
from merlin.composite import chips_and_specs
from merlin.composite import locate
from merlin.functions import timed
import logging

logger = logging.getLogger(__name__)


def sort(chips, key=lambda c: c['acquired']):
    """Sorts all the returned chips by date.

    Args:
        chips: sequence of chips

    Returns:
        sorted sequence of chips
    """

    return tuple(f.rsort(chips, key=key))


def add_dates(dates, dods, key='dates'):
    """Inserts dates into each subdictionary of the parent dictionary.

    Args:
        dod: A dictionary of dictionaries
        dates: A sequence of dates
        key: Subdict key where dates values is inserted

    Returns:
        An updated dictionary of dictionaries with
    """

    def update(d, v):
        d.update({key: v})
        return d

    return {k: update(v, dates) for k, v in dods.items()}


def identify(chip_x, chip_y, rod):
    """Adds chip ids (chip_x, chip_y) to the key for each dict entry

    Args:
        chip_x: x coordinate that identifies the source chip
        chip_y: y coordinate that identifies the source chip
        rod: dict of (x, y): [values]

    Returns:
        dict: {(chip_x, chip_y, x, y): [values]}
    """

    return {(chip_x, chip_y, k[0], k[1]): v for k, v in rod.items()}


def symmetric_dates(dates):
    """Returns a sequence of dates for chips that should be included in
    downstream functions.  May raise Exception.

    Args:
        dates: {key: [datestrings,]}

    Returns:
        Sequence of date strings or Exception

    Example:

        >>> symmetrical_dates({"red":  [ds3, ds1, ds2],
                               "blue": [ds2, ds3, ds1]})
        [2, 3, 1]
        >>>
        >>> symmetrical_dates({"red":  [ds3, ds1],
                               "blue": [ds2, ds3, ds1]})
        Exception: red:[3, 1] does not match blue:[2, 3, 1]
    """

    def check(a, b):
        """Reducer for efficiently comparing two unordered sequences.
        Executes in linear(On) time.

        Args:
            a: {k:[datestring1, datestring2...]}
            b: {k:[datestring2, datestring1...]}

        Returns:
            b if a == b, else Exception with details
        """

        if f.seqeq(second(a), second(b)):
            return b
        else:
            msg = ('assymetric dates detected - {} != {}'
                   .format(first(a), first(b)))
            msga = '{}{}'.format(first(a), second(a))
            msgb = '{}{}'.format(first(b), second(b))
            raise Exception('\n\n'.join([msg, msga, msgb]))

    return second(reduce(check, dates.items()))


def refspec(cas):
    """Returns the first chip spec from the first key to use as a reference.

    Args:
        cas: chips and specs {key: [chips],[specs]}

    Returns:
        dict: chip spec
    """

    return first(second(cas[first(cas)]))


def pyccd_format(chip_x, chip_y, chip_locations, chips_and_specs, dates):
    """Builds inputs for the pyccd algorithm.

    Args:
        chip_x: x coordinate for chip identifier
        chip_y: y coordinate for chip identifier
        chip_locations: chip shaped 2d array of projection coordinates
        chips_and_specs: {k: [chips],[specs]}
        dates: sequence of chip dates to be included in output

    Returns:
        A tuple of tuples.

    Description:
        The pyccd format requires a key of (chip_x, chip_y, x, y) with a
        dictionary of sorted numpy arrays representing each spectra plus an
        additional sorted dates array.

        >>> pyccd_format(*args)
        (((chip_x, chip_y, x1, y1), {"dates": [],  "reds": [],
                                     "greens": [], "blues": [],
                                     "nirs1": [],  "swir1s": [],
                                     "swir2s": [], "thermals": [],
                                     "quality": []}),
         ((chip_x, chip_y, x1, y2), {"dates": [],  "reds": [],
                                     "greens": [], "blues": [],
                                     "nirs1": [],  "swir1s": [],
                                     "swir2s": [], "thermals": [],
                                     "quality": []}))
        ...
    """

    rods = add_dates(list(map(mdates.to_ordinal, sort(dates, key=None))),
                         f.flip_keys(
                             {k: identify(
                                     chip_x,
                                     chip_y,
                                     mrods.locate(
                                         chip_locations,
                                         mrods.from_chips(
                                             chips.to_numpy(
                                                 sort(chips.deduplicate(
                                                          chips.trim(first(v),
                                                                     dates))),
                                                 specs.byubid(second(v))))))
                              for k, v in chips_and_specs.items()}))

    return tuple((k, v) for k, v in rods.items())


def errorhandler(msg='', raises=False):
    """Constructs, logs and raises error messages

    Args:
        msg: Custom message string
        raises: Whether to raise an exception or not

    Returns:
        exception handler function
    """

    def handler(e):
        """logs and raises exception messages

        Args:
            e: An exception or string

        Returns:
            Error message or raises Exception
        """

        msg2 = ' '.join([msg, 'Exception: {}'.format(e)])

        if do(logger.error, msg2) and raises:
            raise Exception(msg2)
        else:
            return msg2
    return handler


def create(point,  chips_url, acquired, queries, chips_fn=chips.get,
           dates_fn=symmetric_dates, format_fn=pyccd_format,
           specs_fn=specs.get):
    """Queries data, performs date filtering/checking and formats the results.

    Args:
        point:     Tuple of (x, y) which is within the extents of a chip
        chips_url: URL to the chips host:port/context
        acquired:  Date range string as start/end, ISO 8601 date format
        queries:   dict of URL queries to retrieve chip specs keyed by
                   spectra
        chips_fn:  Function that accepts x, y, acquired, url, ubids and
                   returns chips.
        dates_fn:  Function that accepts dict of {spectra: [specs],[chips]}
                   and returns a sequence of dates that should be included
                   in the time series.
                   May raise an Exception to halt time series construction.
        format_fn: Function that accepts chip_x, chip_y, chip_locations,
                   chips_and_specs, dates and returns it's representation
                   of a time series.
        specs_fn:  Function that accepts a url query and returns chip specs

    Returns:
        Return value from format_fn
    """

    cas_fn = partial(chips_and_specs,
                     point=point,
                     specs_fn=specs_fn,
                     chips_url=chips_url,
                     chips_fn=chips_fn,
                     acquired=acquired)

    msg = ('point:{} specs_fn:{} '
           'chips_url:{} acquired:{} '
           'queries:{} dates_fn:{} '
           'format_fn:{}').format(point, specs_fn, chips_url,
                                  acquired, queries,
                                  dates_fn, format_fn)

    timed_cas_fn  = timed(excepts(Exception,
                                  cas_fn,
                                  errorhandler(msg, raises=True)))

    safe_dates_fn = excepts(Exception,
                            dates_fn,
                            errorhandler(msg, raises=True))

    cas = {k: timed_cas_fn(query=v) for k, v in queries.items()}

    return format_fn(*locate(point, refspec(cas)),
                     cas,
                     safe_dates_fn(mdates.from_cas(cas)))
