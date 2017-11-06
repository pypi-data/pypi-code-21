from . import core
from . import cli
from . import plugins

# auto import Task subclasses from plugins
def _discover_plugins():
    import pkgutil
    import importlib
    for _, modname, ispkg in pkgutil.iter_modules(plugins.__path__):
        if ispkg or modname.startswith('_'):
            continue
        module = importlib.import_module('.' + modname, plugins.__name__)
        core.register_plugin_module(module)
_discover_plugins()

