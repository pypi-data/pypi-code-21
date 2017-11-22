"""
Falkonry Client

Client to access Condition Prediction APIs

:copyright: (c) 2016 by Falkonry Inc.
:license: MIT, see LICENSE for more details.

"""

import json


class Signal:
    """Signal schema class"""

    def __init__(self, **kwargs):
        self.raw = kwargs.get('signal') if 'signal' in kwargs else {}

    def get_tagIdentifier(self):
        return self.raw['tagIdentifier'] if 'tagIdentifier' in self.raw else None

    def set_tagIdentifier(self, tagIdentifier):
        self.raw['tagIdentifier'] = tagIdentifier
        return self

    def get_delimiter(self):
        return self.raw['delimiter'] if 'delimiter' in self.raw else None

    def set_delimiter(self, delimiter):
        self.raw['delimiter'] = delimiter
        return self

    def get_valueIdentifier(self):
        return self.raw['valueIdentifier'] if 'valueIdentifier' in self.raw else None

    def set_valueIdentifier(self, valueIdentifier):
        self.raw['valueIdentifier'] = valueIdentifier
        return self

    def get_isSignalPrefix(self):
        return self.raw['isSignalPrefix'] if 'isSignalPrefix' in self.raw else None

    def set_isSignalPrefix(self, isSignalPrefix):
        self.raw['isSignalPrefix'] = isSignalPrefix
        return self

    def to_json(self):
        return json.dumps(self.raw)
