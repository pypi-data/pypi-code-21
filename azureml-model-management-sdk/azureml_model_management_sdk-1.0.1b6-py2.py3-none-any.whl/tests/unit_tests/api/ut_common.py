# --------------------------------------------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License. See License.txt in the project root for license information.
# --------------------------------------------------------------------------------------------

import os
import sys
import unittest


class UnitTestBase(unittest.TestCase):
    tests_folder = os.path.dirname(os.path.abspath(__file__))

    def compareCollection(self, expected, actual):
        if sys.version_info[0] == 3:
            self.assertCountEqual(expected, actual)
        else:
            self.assertItemsEqual(expected, actual)
