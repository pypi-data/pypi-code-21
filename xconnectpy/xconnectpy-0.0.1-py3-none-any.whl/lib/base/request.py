#!/usr/bin/python

from xconnectpy.lib.base import *


class Request:

    def __init__(self, resource: str, payload: str = "", reference={}):
        self.resource = resource
        self.payload = payload
        self.reference = reference
