from __future__ import absolute_import, division, print_function
import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError

import os


class FileExists(tester.Tester):

    def __init__(self, exists, test_value=None, kill_on_failure=False, description_group=None, description=None):
        if description is None:
            if exists:
                description = 'Checking that file "{0}" exists'.format(
                    tester.get_name(test_value))
            else:
                description = 'Checking that file "{0}" does not exists'.format(
                    tester.get_name(test_value))
        super(FileExists, self).__init__(value=exists,
                                         test_value=test_value,
                                         kill_on_failure=kill_on_failure,
                                         description_group=description_group,
                                         description=description)

    def test(self, eventinfo, **kw):
        filename = self._GetContent(eventinfo)
        if os.path.isfile(filename):
            if self.Value:
                self.Result = tester.ResultType.Passed
                self.Reason = 'File "{0}" exists'.format(self.TestValue)
            else:
                self.Result = tester.ResultType.Failed
                self.Reason = 'File "{0}" exists and it should not'.format(
                    self.TestValue)
        else:
            if self.Value:
                self.Result = tester.ResultType.Failed
                self.Reason = 'File "{0}" does not exists and it should'.format(
                    self.TestValue)
            else:
                self.Result = tester.ResultType.Passed
                self.Reason = 'File "{0}" does not exists'.format(
                    self.TestValue)
        host.WriteVerbose(["testers.FileExists", "testers"], "{0} - ".format(
            tester.ResultType.to_color_string(self.Result)), self.Reason)
