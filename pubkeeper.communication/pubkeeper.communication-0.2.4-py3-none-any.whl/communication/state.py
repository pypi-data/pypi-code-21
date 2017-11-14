"""
    Copyright 2017 n.io Innovation, LLC | Patent Pending
"""
from enum import IntEnum


class CommState(IntEnum):  # pragma: no cover
    READY = 1
    CONNECTING = 2
    CONNECTED = 3
    CLOSED = 4
