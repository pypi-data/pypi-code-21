# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Hijacking strategies
"""

from .base import BaseStrategy
from .dbapi2 import DBApi2Strategy
from .import_hook import ImportHookStrategy
from .psycopg2 import Psycopg2Strategy
from .flask import FlaskStrategy
from .django import DjangoStrategy
from .pyramid import PyramidStrategy

__all__ = ['BaseStrategy', 'DBApi2Strategy', 'ImportHookStrategy',
           'Psycopg2Strategy', 'FlaskStrategy', 'DjangoStrategy',
           'PyramidStrategy']
