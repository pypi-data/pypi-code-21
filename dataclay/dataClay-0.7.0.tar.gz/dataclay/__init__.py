"""Common Python package.

Note that the client "entrypoint" is the package dataclay.api. Importing it
ensures proper initialization of client-side stuff.

The Execution Environment should take care of the RuntimeType and then call the
dataclay.core.initialize function.
"""
import logging

from .runtime_classes import ProxyRuntime, RuntimeType


__author__ = 'Alex Barcelo <alex.barcelo@bsc.es>'
__copyright__ = '2015 Barcelona Supercomputing Center (BSC-CNS)'

logger = logging.getLogger(__name__)

__all__ = ['DataClayObject', 'StorageObject', 'dclayMethod', 'runtime']


runtime = ProxyRuntime()

# Those need the runtime
from .managers.classes import DataClayObject, dclayMethod
StorageObject = DataClayObject  # Redundant alias

# Ensure definition of basic YAML stuff
from .core.management import _uuid
