from .util import parse_datetime


class Resolution:
    __slots__ = ('_result', 'collected', 'first_seen', 'last_seen',
                 'record_hash', 'rtype', 'resolve', 'resolve_type', 'sources',
                 'query')

    def __init__(self, result):
        self._result = result
        self.collected = parse_datetime(result['collected'])
        self.first_seen = parse_datetime(result['firstSeen'])
        self.last_seen = parse_datetime(result['lastSeen'])
        self.record_hash = bytes.fromhex(result['recordHash'])
        self.rtype = result['recordType']
        self.resolve = result['resolve']
        self.resolve_type = result['resolveType']
        self.sources = result['source']
        self.query = result['value']

    def __repr__(self):
        return (
            'Resolution(query={self.query!r}, resolve={self.resolve!r}, '
            'rtype={self.rtype!r})'.format(self=self)
        )
