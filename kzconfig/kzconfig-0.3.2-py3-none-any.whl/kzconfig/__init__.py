"""
kzconfig
~~~~~

Kazoo config library.

Kazoo configuration library for configuring kazoo within a kubernetes cluster.
This library includes a sup cli command for invoking sup against a remote
kazoo container.
"""

import json
from collections import OrderedDict

from . import meta, util, context, couch, kazoo, sup, dns, cli
from .context import Context

__title__ = 'kzconfig'
__version__ = '0.3.2'
__author__ = "Joe Black <me@joeblack.nyc>"
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2017 Joe Black'


# monkeypatch json to preserve order of keys
json._default_decoder = json.JSONDecoder(
    object_hook=None,
    object_pairs_hook=OrderedDict
)
