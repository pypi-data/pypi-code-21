#!/usr/bin/python

import json

from xconnectpy.lib.base import Facet
from xconnectpy.lib.sitecore import EmailAddress


class EmailAddressList(Facet):

    DefaultFacetKey = "Emails"

    def __init__(self, PreferredEmail:EmailAddress, PreferredKey:str, Others=[]):
        self.PreferredEmail = PreferredEmail
        self.PreferredKey = PreferredKey
        self.Others = Others

    def serialize(self):
        obj = self.__dict__
        obj['PreferredEmail'] = self.PreferredEmail.__dict__

        return json.dumps(obj)
