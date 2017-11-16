"""Optional and extended functionality.

This sub-module provides integration with popular third-party libraries
including `NumPy <http://www.numpy.org/>`_ and `IPython
<https://ipython.org/>`_. These will be ignored if the required dependencies
are not installed. To enable extensions, you can install the required
dependencies with pip:

    cd pytecplot
    python -m pip install -U .[extras]

"""
from __future__ import absolute_import

import logging
from textwrap import dedent

log = logging.getLogger(__name__)

try:
    from ..data.array import Array
    from .numpy import as_numpy_array
    Array.as_numpy_array = as_numpy_array
except ImportError as e:
    log.info(dedent('''
        Could not setup numpy array conversion methods.
        Requred package: numpy'''))

try:
    from . import ipython
except ImportError as e:
    log.info(dedent('''\
        Could not setup tecplot.extensions.ipython.show()
        Required packages: ipython and pillow (Python Image Library)'''))
    log.info(e)
