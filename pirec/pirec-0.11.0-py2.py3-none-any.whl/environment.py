"""Module containing the get_environment function."""

import os
try:
    import pip
except ImportError:
    pass
import socket


def get_environment():
    """Obtain information about the executing environment.

    Captures:
        * installed Python packages using pip (if available),
        * hostname
        * uname
        * environment variables

    Returns:
        dict: a dict with the keys ``python_packages``, ``hostname``, ``uname`` and ``environ``
    """
    env = {}
    try:
        env['python_packages'] = [str(p) for p in pip.get_installed_distributions()]
    except:  # pylint: disable=bare-except
        pass
    env['hostname'] = socket.gethostname()
    env['uname'] = os.uname()
    env['environ'] = dict(os.environ)
    return env
