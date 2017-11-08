""" Utility for temporal coverage
"""
import re
from zope.interface import implements
from eea.alchemy.interfaces import IDiscoverTemporalCoverage

class DiscoverTemporalCoverage(object):
    """ Discover time periods
    """
    implements(IDiscoverTemporalCoverage)

    def __call__(self, text=""):
        pattern = re.compile(r'[12][0189]\d\d\s*\-\s*[12][0189]\d\d')
        found = pattern.findall(text)
        found = [time.replace(' ', '') for time in found]

        res = {}
        for time in found:
            res.setdefault(time, 0)
            res[time] += 1

        items = res.items()
        items.sort()
        for time, count in items:
            yield {
                'count': count,
                'type': 'Time',
                'text': time,
                'relevance': '100.0'
            }
