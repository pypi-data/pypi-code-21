# -*- coding: utf-8 -*-
from .__version import __version__
from .mochila import Sequence, Set, OrderedSet, Bag, MultiSet
import logging

__author__ = 'Horacio Hoyos Rodriguez'
__copyright__ = 'Copyright , Kinori Technologies'

try:
    from logging import NullHandler
except ImportError:
    class NullHandler(logging.Handler):
        def emit(self, record):
            pass

logging.getLogger(__name__).addHandler(NullHandler())