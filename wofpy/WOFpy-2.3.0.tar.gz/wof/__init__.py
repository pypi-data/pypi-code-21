# The version as used in the setup.py
from __future__ import (absolute_import, division, print_function)

from wof.core import _SERVICE_PARAMS, _TEMPLATES, site_map

from wof.core_1_0 import WOF
from wof.core_1_1 import WOF_1_1


__all__ = [
    _SERVICE_PARAMS,
    _TEMPLATES,
    site_map,
    WOF,
    WOF_1_1,
]

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions
