"""
=============
Yo Modules
=============

Python 3 modules for atmospheric research, especially airborne sunphotometry.

.. moduleauthor:: Yohei Shinozuka

"""
# from __future__ import division, absolute_import, print_function

from .codes4data import *
from .codes4figures import *
from _version import __version__ # after https://stackoverflow.com/questions/458550/standard-way-to-embed-version-into-python-package

# __all__ = ['codes4data', 'codes4figures']
# __all__ += codes4data.__all__
# __all__ += codes4figures.__all__

# from numpy.testing import Tester
# test = Tester().test
# bench = Tester().bench
