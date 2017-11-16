from __future__ import unicode_literals, with_statement

import os
import platform
import re
import sys

from contextlib import contextmanager
from ctypes import *
from tempfile import NamedTemporaryFile
from textwrap import dedent

import unittest
from unittest.mock import patch, Mock, PropertyMock
import test
from test import patch_tecutil

import tecplot as tp
from tecplot import layout
from tecplot.exception import *
from tecplot.constant import *

class TestNumpy(unittest.TestCase):
    def test_copy(self):
        #frame = tp.active_frame()
        # create dataset
        # copy dataset out to numpy
        # verify
        try:
            from tecplot.data import create_ordered_zone
            self.assertTrue(False, 'numpy not tested yet, but data creation is there')
        except ImportError:
            pass

if __name__ == '__main__':
    from .. import main
    main()
