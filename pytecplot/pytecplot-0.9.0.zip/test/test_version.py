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

from test import patch_tecutil

import tecplot as tp

class TestVersion(unittest.TestCase):
    def test_version(self):
        self.assertIsInstance(tp.version_info, tp.version.Version)
        self.assertRegex(tp.__version__, '\d+\.\d+\.\d+')

    def test_sdk_version(self):
        self.assertIsInstance(tp.sdk_version_info,
                              tp.tecutil.tecutil_connector.SDKVersion)
        self.assertRegex(tp.sdk_version, '\d+\.\d+-\d+-\d+')


if __name__ == '__main__':
    from . import main
    main()
