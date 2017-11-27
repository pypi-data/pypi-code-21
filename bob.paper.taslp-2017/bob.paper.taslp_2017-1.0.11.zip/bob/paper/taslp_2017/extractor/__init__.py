#!/usr/bin/env python
# vim: set fileencoding=utf-8 :

"""Feature extraction tools"""

from .SpectralStatistics import SpectralStatistics

# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
