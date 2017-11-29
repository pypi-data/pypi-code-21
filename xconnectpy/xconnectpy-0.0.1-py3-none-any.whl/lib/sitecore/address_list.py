#!/usr/bin/python

import json

from xconnectpy.lib.base import Facet
from xconnectpy.lib.sitecore import Address


class AddressList(Facet):

    DefaultFacetKey = "Addresses"

    def __init__(self, PreferredAddress:Address, PreferredKey:str, Others=[]):
        self.PreferredAddress = PreferredAddress
        self.PreferredKey = PreferredKey
        self.Others = Others

    def serialize(self):
        obj = self.__dict__.copy()
        obj['PreferredAddress'] = self.PreferredAddress.__dict__

        return json.dumps(obj)
