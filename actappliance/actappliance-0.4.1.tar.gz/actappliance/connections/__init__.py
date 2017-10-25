from __future__ import print_function, division, unicode_literals, absolute_import

# Hoist classes and functions into connection namespace
from actappliance.connections.rest import ApplianceRest  # NOQA
from actappliance.connections.ssh import ApplianceSsh    # NOQA

# Set default logging handler to avoid "No handler found" warnings.
import logging
try:  # Python 2.7+
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())
