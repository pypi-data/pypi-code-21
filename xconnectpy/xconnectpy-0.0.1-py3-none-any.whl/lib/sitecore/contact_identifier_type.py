#!/usr/bin/python

from enum import Enum


class ContactIdentifierType(Enum):
    Known = "Known"
    Anonymous = "Anonymous"
    Empty = ""
