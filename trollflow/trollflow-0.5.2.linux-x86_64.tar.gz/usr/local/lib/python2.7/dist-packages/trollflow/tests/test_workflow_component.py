#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

"""Unit testing for workflow_component
"""

import unittest

from trollflow.workflow_component import AbstractWorkflowComponent


class Foo(AbstractWorkflowComponent):

    def __init__(self):
        super(Foo, self).__init__()

    def pre_invoke(self):
        pass

    def invoke(self):
        pass

    def post_invoke(self):
        pass


class TestWorkflowComponent(unittest.TestCase):

    component = Foo()

    def test_init(self):
        self.assertEqual(len(self.component.slots), 0)
        self.assertFalse(self.component.use_lock)

    def test_pre_invoke(self):
        self.assertIsNone(self.component.pre_invoke())

    def test_invoke(self):
        self.assertIsNone(self.component.invoke())

    def test_post_invoke(self):
        self.assertIsNone(self.component.post_invoke())


def suite():
    """The suite for test_workflow_component
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWorkflowComponent))

    return mysuite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
