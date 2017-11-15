import importlib
import threading
import time

safe_names = []

def munge(namespace='__main__'):
    """Precedes all names in 'namespace' with 'prefix'."""

    module = importlib.import_module(namespace)
    global safe_names
    if not safe_names:
        safe_names.extend(vars(module).keys())

    prefix = '__{}__'.format(namespace)
    to_munge = {name: val for name, val in vars(module).items() if name not in safe_names}
    for name, val in to_munge.items():
        setattr(module, prefix + name, val)
        delattr(module, name)
        safe_names.append(prefix + name)


def run_continuously(fun):
    """A decorator utility that runs a function repeatedly.  Good for threads."""
    def wrapper():
        while True:
            fun()
            time.sleep(.00001)
    return wrapper


def automunge():
    """Start a thread that repeatedly calls munge()"""
    thread = threading.Thread(daemon=True, target=run_continuously(munge))
    thread.start()
