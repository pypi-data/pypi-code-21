"""
Utilities for loading and doing calculations with a partner's hours of
operations configration.
"""
import pytz

from dateutil.tz import tzlocal

from codado.py import utcnowTZ, parseDate


class HoursError(Exception):
    """
    There was an invalid hours of operation setting
    """


def hoursFromConfig(originalHours):
    """
    Return the data structure for hours of operation.
    'close' and 'open' are lists of times (e.g. 'Monday 8:00 PST').
    'default' is a dict containing 'open' and 'close' times to use when
    not specified for any given day of the week.
    """
    hours = {'close': [],
             'open': [],
             'default': {}}
    specifiedDays = set()

    hrs = dict((key, value) for key, value in originalHours.iteritems() if key != 'timezone')
    if hrs:
        for day, times in hrs.items():
            if times.get('open') and times.get('close') and \
               parseDate(times['open']).time() >= parseDate(times['close']).time():
                raise HoursError('Open time incorrectly set after close time for %s' % day)
            for closeOrOpen, time in times.items():
                if day == 'default' and time:
                    hours['default'][closeOrOpen] = time
                elif time:
                    hours[closeOrOpen].append(day + ' ' + time)
                    specifiedDays.add(parseDate(day).weekday())

        # there must be a default value if some days are unspecified
        if len(specifiedDays) < 7 and not originalHours.get('default'):
            raise HoursError('Missing hours of operation for at least one weekday')

        # for each weekday that was not specified, set it to the default
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for day in days:
            if parseDate(day).weekday() not in specifiedDays:
                if hours['default'].get('close'):
                    hours['close'].append(day + ' ' + hours['default']['close'])
                if hours['default'].get('open'):
                    hours['open'].append(day + ' ' + hours['default']['open'])
    
    return hours


def hoursDatetime(hours, timezone):
    """
    Return a dictionary with datetime versions of the opening and
    closing time for today in UTC.
    Expects "hours" to be in the format returned by hoursFromConfig.
    """
    openTime = None
    closeTime = None

    timezone = pytz.timezone(timezone)
    rightNow = utcnowTZ().astimezone(timezone)
    today = rightNow.weekday()

    # open time for the current day
    for o in hours['open']:
        t = timezone.localize(parseDate(o))
        if today == t.weekday():
            openTime = t.astimezone(pytz.utc)
            break

    # close time for the current day
    for c in hours['close']:
        t = timezone.localize(parseDate(c))
        if today == t.weekday():
            closeTime = t.astimezone(pytz.utc)
            break

    return {'open': openTime,
            'close': closeTime}


def hoursOfOperation(hours, timezone):
    """
    Return a dictionary of relevant times for the current day.
    Expects "hours" to be in the format returned by hoursFromConfig.
    """
    fmt = '%A %I:%M %p %Z'
    operatingHours = hoursDatetime(hours, timezone)

    timezone = pytz.timezone(timezone)
    rightNow = utcnowTZ().astimezone(timezone)

    if operatingHours['open'] or operatingHours['close']:
        nextOpen = None
        pastClosed = False
        if operatingHours['close']:
            pastClosed = operatingHours['close'] < rightNow.astimezone(pytz.utc)

        if pastClosed:
            i = 1
            while not nextOpen and i < 7:
                for o in hours['open']:
                    t = timezone.localize(parseDate(o))
                    if (rightNow.weekday() + i) % 7 == t.weekday():
                        nextOpen = t
                        break
                i += 1

        # reformat back to local timezone
        formatter = lambda x: x.astimezone(tzlocal()).strftime(fmt) if x else None

        closeTime = formatter(operatingHours['close'])
        openTime = formatter(operatingHours['open'])
        nextOpen = formatter(nextOpen) if nextOpen else None

        openLater = False
        if operatingHours['open']:
            openLater = rightNow.astimezone(pytz.utc) < operatingHours['open']
        currentlyClosed = openLater or pastClosed
    else:
        # no hours were set,
        # therefore medicalGroup is opened 24/7
        openTime = operatingHours['open']
        closeTime = operatingHours['close']
        nextOpen = None
        openLater = None
        currentlyClosed = None

    return {'close': closeTime,
            'open': openTime,
            'nextOpen': nextOpen,
            'openLater': openLater,
            'currentlyClosed': currentlyClosed
            }