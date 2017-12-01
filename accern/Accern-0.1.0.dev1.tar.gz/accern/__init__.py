"""Accern: python library for Accern API.

Accern is a python library to query, download, filter and save Accern
Data.
"""

from accern.stream import Stream, StreamListener

token = None


__all__ = [
    'Stream',
    'StreamListener'
]
