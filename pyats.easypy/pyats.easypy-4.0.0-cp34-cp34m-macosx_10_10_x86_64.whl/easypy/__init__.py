# metadata
__version__ = '4.0.0'
__author__ = 'Cisco Systems'
__contact__ = 'pyats-support-ext@cisco.com'
__copyright__ = 'Copyright (c) 2017, Cisco Systems Inc.'

from .main import _default_runtime, main
from operator import attrgetter as _attrgetter

globals().update((name.split('.')[-1], _attrgetter(name)(_default_runtime))
                 for name in _default_runtime.__all__)

__all__ = ['main', ]
__all__.extend(name.split('.')[-1] for name in _default_runtime.__all__)

