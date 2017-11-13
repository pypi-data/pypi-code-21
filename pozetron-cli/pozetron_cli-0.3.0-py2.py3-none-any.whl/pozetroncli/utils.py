from collections import Counter
import hashlib
import os

import dateutil.tz
from pydicti import dicti
import pytz
from pytz.exceptions import UnknownTimeZoneError


def _get_timezone_aliases():
    """
    Builds and returns case-insensitive dict of timezone name aliases.
    {alias: tz_name}
    """
    result = dicti()
    # Add short names for non-ambiguous common timezones
    # Example: 'London' -> 'Europe/London'
    # US timezones get special treatment, e.g. 'Pacific' is 'US/Pacific' by default.
    counter = Counter(x.split('/')[-1] for x in pytz.common_timezones)
    for tz_name in pytz.common_timezones:
        alias = tz_name.split('/')[-1]
        if counter[alias] > 1 and not tz_name.startswith('US/'):
            continue
        result[alias] = tz_name
    # Add itself (just for case-insensitivity)
    for tz_name in pytz.common_timezones:
        result[tz_name] = tz_name
    return result


_TIMEZONE_ALIASES = _get_timezone_aliases()
# Add more timezones below (case-insensitive)
_TIMEZONE_ALIASES.update({
    # United States
    'EST': 'US/Eastern',
    'CST': 'US/Central',
    'MST': 'US/Mountain',
    'PST': 'US/Pacific',
    'AKST': 'US/Alaska',
    'HAST': 'US/Hawaii',
})
_TIMEZONE_LOCAL = ('local', 'localtime')


def get_timezone(tz_name):
    """
    Returns timezone object that can be used in`datetime.astimezone` call.
    """
    tz_name = tz_name.replace(' ', '_')
    # Special treatment for local timezone
    if tz_name.lower() in _TIMEZONE_LOCAL:
        return dateutil.tz.tzlocal()
    # Check if it's an alias (also avoid lowercase/uppercase problems)
    try:
        tz_name = _TIMEZONE_ALIASES[tz_name]
    except KeyError:
        pass
    # Finally, get timezone
    try:
        return pytz.timezone(tz_name)
    except UnknownTimeZoneError as ex:
        raise ValueError('Unknown timezone: {}'.format(ex.args[0]))


def random_sha256():
    hasher = hashlib.new('sha256')
    hasher.update(os.urandom(16))
    return hasher.hexdigest()
