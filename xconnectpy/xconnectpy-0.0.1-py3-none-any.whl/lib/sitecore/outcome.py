#!/usr/bin/python

import json
from collections import OrderedDict

from xconnectpy.lib.base import Entity
from xconnectpy.lib.util import Guid


class Outcome(Entity):

    def __init__(self, DefinitionId: str, Timestamp: str, CurrencyCode: str, MonetaryValue: float, Id: str = ""):
        self.DefinitionId = DefinitionId
        self.Timestamp = Timestamp
        self.CurrencyCode = CurrencyCode
        self.MonetaryValue = MonetaryValue

        if Id:
            self.Id = Id
        else:
            self.Id = Guid.generate()

    def serialize(self):

        obj = OrderedDict([
            ('@odata.type', '#Sitecore.XConnect.Outcome'),
            ('CustomValues', []),
            ('DefinitionId', self.DefinitionId),
            ('Id', self.Id),
            ('Timestamp', self.Timestamp),
            ('CurrencyCode', self.CurrencyCode),
            ('MonetaryValue', self.MonetaryValue)
        ])

        return obj
