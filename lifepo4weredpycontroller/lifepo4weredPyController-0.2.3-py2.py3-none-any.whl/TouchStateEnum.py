#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class touchStateEnum(Enum):
    unknown = -1
    inactive = 0
    start = 3
    stop = 12
    held = 15
