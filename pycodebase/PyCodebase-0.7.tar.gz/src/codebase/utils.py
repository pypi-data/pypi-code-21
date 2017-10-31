import datetime
import re


# Taken from https://docs.python.org/2/library/datetime.html
ZERO = datetime.timedelta(0)


class UTC(datetime.tzinfo):
    """UTC"""

    def utcoffset(self, dt):
        return ZERO

    def tzname(self, dt):
        return "UTC"

    def dst(self, dt):
        return ZERO

utc = UTC()


class FixedOffset(datetime.tzinfo):
    """Fixed offset in minutes east from UTC."""

    def __init__(self, offset, name):
        self.__offset = datetime.timedelta(minutes=offset)
        self.__name = name

    def utcoffset(self, dt):
        return self.__offset

    def tzname(self, dt):
        return self.__name

    def dst(self, dt):
        return ZERO



dt_pattern = re.compile(
    r'(\d{4})-(\d{2})-(\d{2})T' # 2016-01-02T
    r'(\d{2}):(\d{2}):(\d{2})' # 03:04:05
    r'([Z+-])((\d{2}):(\d{2}))?' # Z or +01:00 or -01:00
)


def parse_date(value):
    """Parse a string, returning a time zone-aware datetime instance.

    If the value is an invalid format the original value is returned.

    >>> parse_date('2016-01-02T03:04:05Z')
    datetime.datetime(2016, 1, 2, 3, 4, 5, tzinfo=<codebase.utils.UTC ...>) # doctest: +ELLIPSIS
    >>> parse_date('2016-01-02T03:04:05')
    '2016-01-02T03:04:05'
    >>> parse_date('foo')
    'foo'
    >>> parse_date(None)
    >>>
    """

    if not isinstance(value, basestring):
        return value

    match = dt_pattern.search(value)

    if match:
        components = [int(o) for o in match.groups()[:6]]
        dt = datetime.datetime(*components)

        if match.group(7) == 'Z':
            tz = utc

        else:
            # It's a fixed offset like '+11:59'.
            hours, minutes = int(match.group(9)), int(match.group(10))
            offset = (hours * 60) + minutes

            if match.group(7) == '-':
                # It's a negative fixed offset like '-11:59'.
                offset = offset * -1

            name = match.group(7) + match.group(8)
            tz = FixedOffset(offset, name)

        dt = dt.replace(tzinfo=tz)

        return dt

    else:
        return value


def format_since_dt(value):
    """Convert a datetime to UTC and returns a string to use with the activity
    feed's `since` keyword argument.
    """
    # Actually the API seems to parse dates too.

    try:
        value = value.astimezone(utc)
    except ValueError:
        # Naive datetime, we assume it is meant for UTC.
        value = value.replace(tzinfo=utc)

    # '2014-09-26 17:26:47 +0000'
    result = value.strftime('%Y-%m-%d %H:%M:%S +0000')

    return result


def build_create_note_payload(assignee_id=None, category_id=None, content=None,
        milestone_id=None, priority_id=None, private=None, status_id=None,
        summary=None, time_added=None, upload_tokens=None):
    """Return a dict to use when creating a ticket note (or for changing a
    ticket's properties).
    """
    payload = {
        'content': content,
        'private': private,
        'time_added': time_added,
        'upload_tokens': upload_tokens,

    }

    changes = {
        'assignee_id': assignee_id,
        'category_id': category_id,
        'milestone_id': milestone_id,
        'priority_id': priority_id,
        'status_id': status_id,
        'summary': summary,
    }

    # And then we remove any keys set to None.
    payload = {k: v for k, v in payload.items() if v is not None}
    changes = {k: v for k, v in changes.items() if v is not None}

    if changes:
        payload['changes'] = changes

    return payload


def build_milestone_payload(deadline=None, description=None, estimated_time=None,
        name=None, parent_id=None, responsible_user_id=None, start_at=None,
        status=None):
    # How many of these fields are actually required I don't know.

    if isinstance(start_at, datetime.date):
        # If they gave us a datetime, chop off the hours, etc.
        start_at = str(start_at)[:10]

    if isinstance(deadline, datetime.date):
        deadline = str(deadline)[:10]

    payload = {
        'deadline': deadline,
        'description': description,
        'estimated_time': estimated_time,
        'name': name,
        'parent_id': parent_id,
        'responsible_user_id': responsible_user_id,
        'start_at': start_at,
        'status': status,
    }

    return payload


def quote_search_value(value):
    """Return a status like 'In progress' as '"In progress"'."""
    value = str(value)
    value = value.replace("'", '')
    value = value.replace('"', '')
    value = u'"%s"' % value

    return value


def iterable(value):
    """True if value is iterable (except for strings)."""
    if isinstance(value, basestring):
        return False

    try:
        iter(value)
    except TypeError:
        return False
    else:
        return True


def build_ticket_search_query(**kwargs):
    """Returns a string for use in a ticket search query.

    Returns an empty string if there are no query parameters.
    """
    params = []

    # Order params, makes testing simpler.
    for key, value in sorted(kwargs.items()):
        if value is None:
            continue

        if not iterable(value):
            value = [value]

        value = ','.join(quote_search_value(v) for v in value)
        term = '%s:%s' % (key, value)
        params.append(term)

    query = ' '.join(params)

    return query


def encode_dict(d, encoding='UTF-8'):
    """Convert unicode and datetime values in a dictionary to encoded strings.

    Useful for writing rows to an instance of csv.DictWriter.
    """
    result = {}

    for k, v in d.items():
        if isinstance(v, unicode):
            v = v.encode(encoding)
        elif isinstance(v, datetime.datetime):
            v = str(v)

        result[k] = v

    return result
