#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017, Panu Lahtinen

# Author(s):

#   Panu Lahtinen <panu.lahtinen@fmi.fi>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""The tests package.
"""

import unittest
# import doctest
from trollflow.tests import (test_utils, test_workflow_component,
                             test_workflow_streamer)


def suite():
    """The global test suite.
    """
    mysuite = unittest.TestSuite()
    # Test the documentation strings
    # mysuite.addTests(doctest.DocTestSuite(image))
    # Use the unittests also
    mysuite.addTests(test_utils.suite())
    mysuite.addTests(test_workflow_component.suite())
    mysuite.addTests(test_workflow_streamer.suite())

    return mysuite
