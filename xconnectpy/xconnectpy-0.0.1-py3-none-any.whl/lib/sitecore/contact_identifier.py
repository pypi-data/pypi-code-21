#!/usr/bin/python

from xconnectpy.lib.base import Entity
from xconnectpy.lib.sitecore import ContactIdentifierType


class ContactIdentifier(Entity):

    def __init__(self, Source: str, Identifier: str,
                 IdentifierType: ContactIdentifierType = ContactIdentifierType.Empty, IsValid: bool = True):
        self.Source = Source
        self.Identifier = Identifier
        self.IsValid = IsValid

        if IdentifierType.value:
            self.IdentifierType = IdentifierType.value
