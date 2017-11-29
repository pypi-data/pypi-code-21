#!/usr/bin/python

from xconnectpy.lib.base import Entity


class IdentifiedContactReference(Entity):
    def __init__(self, Source, Identifier):
        self.Source = Source
        self.Identifier = Identifier
