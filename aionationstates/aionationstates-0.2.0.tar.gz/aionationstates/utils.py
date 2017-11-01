import re
from datetime import datetime, timezone


def normalize(identifier):
    identifier = identifier.lower().replace(' ', '_')
    if not re.match('^[a-z0-9_-]+$', identifier):
        raise ValueError(f'provided identifier {identifier} contains invalid'
                         ' characters.')
    return identifier


def banner_url(id):
    return f'https://www.nationstates.net/images/banners/{id}.jpg'


def timestamp(line):
    return datetime.utcfromtimestamp(int(line))


def utc_seconds(datetime_):
    return int(datetime_.replace(tzinfo=timezone.utc).timestamp())


def unscramble_encoding(text):
    """This is a workaround for a bug in the NS server-side code.
    (This entire lib is, honestly.)

    Specifically, somewhere in the process W-1252 encoded text is
    wrongly interpreted to be ISO-8859-1, resulting in *some*
    characters being deterministically unintentionally replaced with
    useless to the user Unicode control chars.

    This is a very common problem.  Common enough, in fact, to be
    accounted for in the HTML treatment of Character References as
    defined by the specification.  Well, it is technically a parse
    error, but nobody really cares since the correct, expected
    character is returned.  For this reason, the bug is not present
    (or at least not visible) on the NS web interface, and only shows
    itself when dealing with the API.

    Interestingly enough, these characters are not always serialized as
    NCRs, in the dispatch CDATA they are represented literally, meaning
    that even modifying the XML parser to include a bit of HTML
    leniency would not be enough.  Not that anyone would do that
    regardless.


    This function reverses the process, substiuting the unprintable
    mess returned by NS for the Unicode characters it must have
    originated from.

    It's a bit ugly, but gets the job done.
    """
    return (
        text
        .replace('\u0080', '\N{EURO SIGN}')
        .replace('\u0082', '\N{SINGLE LOW-9 QUOTATION MARK}')
        .replace('\u0083', '\N{LATIN SMALL LETTER F WITH HOOK}')
        .replace('\u0084', '\N{DOUBLE LOW-9 QUOTATION MARK}')
        .replace('\u0085', '\N{HORIZONTAL ELLIPSIS}')
        .replace('\u0086', '\N{DAGGER}')
        .replace('\u0087', '\N{DOUBLE DAGGER}')
        .replace('\u0088', '\N{MODIFIER LETTER CIRCUMFLEX ACCENT}')
        .replace('\u0089', '\N{PER MILLE SIGN}')
        .replace('\u008A', '\N{LATIN CAPITAL LETTER S WITH CARON}')
        .replace('\u008B', '\N{SINGLE LEFT-POINTING ANGLE QUOTATION MARK}')
        .replace('\u008C', '\N{LATIN CAPITAL LIGATURE OE}')
        .replace('\u008E', '\N{LATIN CAPITAL LETTER Z WITH CARON}')
        .replace('\u0091', '\N{LEFT SINGLE QUOTATION MARK}')
        .replace('\u0092', '\N{RIGHT SINGLE QUOTATION MARK}')
        .replace('\u0093', '\N{LEFT DOUBLE QUOTATION MARK}')
        .replace('\u0094', '\N{RIGHT DOUBLE QUOTATION MARK}')
        .replace('\u0095', '\N{BULLET}')
        .replace('\u0096', '\N{EN DASH}')
        .replace('\u0097', '\N{EM DASH}')
        .replace('\u0098', '\N{SMALL TILDE}')
        .replace('\u0099', '\N{TRADE MARK SIGN}')
        .replace('\u009A', '\N{LATIN SMALL LETTER S WITH CARON}')
        .replace('\u009B', '\N{SINGLE RIGHT-POINTING ANGLE QUOTATION MARK}')
        .replace('\u009C', '\N{LATIN SMALL LIGATURE OE}')
        .replace('\u009E', '\N{LATIN SMALL LETTER Z WITH CARON}')
        .replace('\u009F', '\N{LATIN CAPITAL LETTER Y WITH DIAERESIS}')
    )


def datetime_to_ns(then: datetime) -> str:
    """Transform a ``datetime`` object into a NationStates-style
    string, for example "6 days ago", "105 minutes ago", etc.
    """
    if then == datetime(1970, 1, 1, 0, 0):
        return 'Antiquity'

    now = datetime.utcnow()
    delta = now - then
    seconds = delta.total_seconds()

    # There's gotta be a better way to do this...
    years,   seconds = divmod(seconds, 60*60*24*365)
    days,    seconds = divmod(seconds, 60*60*24)
    hours,   seconds = divmod(seconds, 60*60)
    minutes, seconds = divmod(seconds, 60)
    years   = int(years)
    days    = int(days)
    hours   = int(hours)
    minutes = int(minutes)
    seconds = round(seconds)

    if years > 1:
        if days > 1:
            return f'{years} years {days} days ago'
        elif days == 1:
            return '{years} years 1 day ago'
        return '{years} years ago'
    if years == 1:
        if days > 1:
            return f'1 year {days} days ago'
        elif days == 1:
            return '1 year 1 day ago'
        return '1 year ago'

    if days > 3:
        return f'{days} days ago'
    if days > 1:
        if hours > 1:
            return f'{days} days {hours} hours ago'
        elif hours == 1:
            return f'{days} days 1 hour ago'
        return f'{days} days ago'
    if days == 1:
        if hours > 1:
            return f'1 day {hours} hours ago'
        elif hours == 1:
            return '1 day 1 hour ago'
        return '1 day ago'

    if hours > 1:
        return f'{hours} hours ago'
    if hours == 1:
        return f'{minutes + 60} minutes ago'

    if minutes > 1:
        return f'{minutes} minutes ago'
    if minutes == 1:
        return '1 minute ago'

    return 'Seconds ago'

