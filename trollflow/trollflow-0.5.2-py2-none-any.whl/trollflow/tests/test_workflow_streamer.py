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

"""Unit testing for WorkflowStreamer
"""

import unittest
from mock import patch
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from trollflow.workflow_streamer import WorkflowStreamer, utils


class Foo(object):

    def __init__(self):
        pass


class TestWorkflowStreamer(unittest.TestCase):

    config_str = """
    Workflow:
      - trollflow.tests.test_workflow_streamer.Foo:
        arg1: 1
        arg2: 2
    """
    fid = StringIO(config_str)
    config = utils.ordered_load(fid)
    fid.close()

    @patch("trollflow.workflow_streamer.workflow_runner")
    def setUp(self, runner):
        self.runner = runner
        self.streamer = WorkflowStreamer(config=self.config)

    def test_init(self):
        self.assertIsNotNone(self.streamer.workflow)
        self.assertIsNone(self.streamer.input_queue)
        self.assertTrue(hasattr(self.streamer.output_queue, 'get'))
        self.assertIsNone(self.streamer.prev_lock)
        self.assertIsNone(self.streamer.lock)

    def test_stop(self):
        self.streamer.stop()
        self.assertFalse(self.streamer._loop)

    # def test_run(self):
    #    self.streamer.input_queue = Queue.Queue()
    #    self.streamer.start()


def suite():
    """The suite for test_workflow_streamer
    """
    loader = unittest.TestLoader()
    mysuite = unittest.TestSuite()
    mysuite.addTest(loader.loadTestsFromTestCase(TestWorkflowStreamer))

    return mysuite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())
