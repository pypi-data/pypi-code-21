#!/usr/bin/env python
# vim: set fileencoding=utf-8 :
# Sushil Bhattacharjee <sushil.bhattacharjee.@idiap.ch>
# Tue 19 Sep 17:16:22 2017

"""
The methods for the package

"""

def get_config():
    """
    Returns a string containing the configuration information.

    """
    import bob.extension
    return bob.extension.get_config(__name__)


# gets sphinx autodoc done right - don't remove it
__all__ = [_ for _ in dir() if not _.startswith('_')]
