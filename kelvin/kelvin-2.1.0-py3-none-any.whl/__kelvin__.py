
# The first Python module run by the executable.  It looks for a module named __kelvinmain__
# (the user's main module) and runs it with the name '__main__'.

import sys
try:
    from pkgutil import get_loader # Python 3
except ImportError:
    from imp import get_loader     # Python 2

def run_main():
    """
    The Kelvin code that runs the application's startup module as __main__.
    """
    # This seems kind of messy.  It is required because Python automatically creates a __main__
    # module in Py_Initialize and we have to run a different module, but fool it into thinking
    # it is __main__.  We do this by running the module, but passing it the dictionary from
    # __main__.

    mod_name = '__kelvinmain__'

    loader   = get_loader(mod_name)
    code     = loader.get_code(mod_name)
    filename = loader.get_filename(mod_name)  # Python 2.7+.  Earlier versions may have _get_filename.

    # # Python 3 has zipmodule.get_filename, but it is unofficial and _get_filename in Python 2.
    # for fname in ('get_filename', '_get_filename'):
    #     func = getattr(loader, fname, None)
    #     if func:
    #         filename = func(mod_name)
    #         break

    globals = sys.modules["__main__"].__dict__

    globals.update(
        __name__    = '__main__',
        __file__    = filename,
        __loader__  = loader,
        __cached__  = None,
        __package__ = None)

    exec(code, globals)
