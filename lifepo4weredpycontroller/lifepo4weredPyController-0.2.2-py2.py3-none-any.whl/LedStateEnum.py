#!/usr/bin/python3
# -*- coding: utf-8 -*-

from enum import Enum, unique


@unique
class ledStateEnum(Enum):
    unknow = -1
    off = 0
    on = 1
    pulsing = 2
    flasing = 3
