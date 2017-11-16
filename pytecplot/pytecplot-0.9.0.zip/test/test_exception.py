from __future__ import unicode_literals, with_statement

import ctypes
import numpy as np
import os
import platform
import re
import sys

from contextlib import contextmanager
from tempfile import NamedTemporaryFile
from textwrap import dedent

import unittest
from unittest.mock import patch, Mock, PropertyMock

from . import patch_tecutil

import tecplot as tp
from tecplot.exception import TecplotOutOfDateEngineError


class TestException(unittest.TestCase):
    def test_sdk_version_error(self):
        vinfo = tp.sdk_version_info
        try:
            tp.sdk_version_info = (0,0,0)

            try:
                raise TecplotOutOfDateEngineError((1,0,0))
                self.assertTrue(False)
            except TecplotOutOfDateEngineError as e:
                self.assertEqual(str(e).split('\n')[-2],
                    '    Minimum version required: 1.0-0')

            try:
                raise TecplotOutOfDateEngineError((1,0,0), 'test')
                self.assertTrue(False)
            except TecplotOutOfDateEngineError as e:
                self.assertEqual(str(e).split('\n')[-1], 'test')

        finally:
            tp.sdk_version_info = vinfo


if __name__ == '__main__':
    from . import main
    main()
