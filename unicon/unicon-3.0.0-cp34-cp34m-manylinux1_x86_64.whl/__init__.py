__version__ = '3.0.0'

from unicon.logs import log
from unicon.eal.expect import Spawn
from unicon.core.pluginmanager import PluginManager
__plugin_manager__ = PluginManager()

# Unicon Connection Factory class
from unicon.bases.connection import Connection

__plugin_manager__.discover_builtin_plugins()
__plugin_manager__.discover_external_plugins()

# import the PyATS topology adapter
try:
    __import__('ats.topology')
except ImportError:
    # Do not complain, this may be a non PyATS setup
    pass
else:
    from unicon.adapters.topology import Unicon, XRUTConnect
