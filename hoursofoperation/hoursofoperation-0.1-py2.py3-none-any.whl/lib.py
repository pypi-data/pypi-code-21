"""
Utilities for loading and doing calculations with a partner's hours of
operations configration.
"""


def hoursFromConfig(self, originalHours):
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
            if times.get('open') and times.get('close'):
                assert parser.parse(times['open']).time() < parser.parse(times['close']).time(), 'Open time incorrectly set after close time for %s' % day
            for closeOrOpen, time in times.items():
                if day == 'default' and time:
                    hours['default'][closeOrOpen] = time
                elif time:
                    hours[closeOrOpen].append(day + ' ' + time)
                    specifiedDays.add(parser.parse(day).weekday())

        # there must be a default value if some days are unspecified
        if len(specifiedDays) < 7:
            assert originalHours['default'], 'Missing hours of operation for at least one weekday'

        # for each weekday that was not specified, set it to the default
        days = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
        for day in days:
            if parser.parse(day).weekday() not in specifiedDays:
                if hours['default'].get('close'):
                    hours['close'].append(day + ' ' + hours['default']['close'])
                if hours['default'].get('open'):
                    hours['open'].append(day + ' ' + hours['default']['open'])
    return hours