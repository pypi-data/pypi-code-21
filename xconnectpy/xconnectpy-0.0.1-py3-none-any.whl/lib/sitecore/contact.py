#!/usr/bin/python

import json
from typing import List

from xconnectpy.lib.base import Entity
from xconnectpy.lib.sitecore import ContactIdentifier
from xconnectpy.lib.util import Guid


class Contact(Entity):

    EntityResource = "Contacts"

    def __init__(self, ConcurrencyToken: str = '', Id: str = "",
                 LastModified: str = '', IsKnown=True, Identifiers: List[ContactIdentifier] = []):

        self.Identifiers = Identifiers
        self.IsKnown = IsKnown

        if ConcurrencyToken:
            self.ConcurrencyToken = ConcurrencyToken
        if LastModified:
            self.LastModified = LastModified
        if Id:
            self.Id = Id
        else:
            self.Id = Guid.generate()
            self.Identifiers.append(ContactIdentifier(Source="Alias", Identifier=self.Id, IsValid=True))

    def serialize(self):
        obj = self.__dict__.copy()

        obj.pop('Id', None)

        if self.Identifiers:
            identifiers = []

            for identifier in self.Identifiers:
                identifiers.append(identifier.__dict__)

            obj['Identifiers'] = identifiers

        return json.dumps(obj)
