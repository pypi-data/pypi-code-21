# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals


class PumpException(Exception):
    """Base exception class"""


class ParameterError(PumpException):
    """Not a valid parameter"""


class TimeoutError(PumpException):
    """Request timed out"""
