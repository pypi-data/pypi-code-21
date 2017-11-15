"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""


class BrewTranslator(object):
    def __init__(self, brewer):
        self._brewer = brewer

    def callback(self, signals):
        self._brewer.brew(signals)  # pragma no cover
