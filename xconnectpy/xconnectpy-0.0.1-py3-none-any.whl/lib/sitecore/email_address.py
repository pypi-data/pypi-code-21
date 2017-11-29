#!/usr/bin/python

from xconnectpy.lib.base import Facet


class EmailAddress(Facet):

    def __init__(self, SmtpAddress: str, Validated: bool):
        self.SmtpAddress = SmtpAddress
        self.Validated = Validated
