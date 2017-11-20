# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals


import sys
from . import uqer
from .uqer import Client
from .mfclient import neutralize, standardize, winsorize, simple_long_only, long_only
from . import DataAPI

from .version import __version__

from .DataAPI import retry_interval, max_retries






