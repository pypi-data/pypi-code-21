"""
kzconfig.cli
~~~~~

Kazoo config library.

A sup cli command for invoking sup against a remote kazoo container.
"""

import click

from ..context import Context
from . import sup, kubectl
