import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError

import os


class DirectoryExists(tester.Tester):

    def __init__(self, exists, test_value=None, kill_on_failure=False, description_group=None, description=None):
        if description is None:
            if exists:
                description = 'Checking that Directory "{0}" exists'.format(
                    tester.get_name(test_value))
            else:
                description = 'Checking that Directory "{0}" does not exists'.format(
                    tester.get_name(test_value))
        super(DirectoryExists, self).__init__(value=exists,
                                              test_value=test_value,
                                              kill_on_failure=kill_on_failure,
                                              description_group=description_group,
                                              description=description)

    def test(self, eventinfo, **kw):
        dirname = self._GetContent(eventinfo)
        if os.path.isdir(dirname):
            if self.Value:
                self.Result = tester.ResultType.Passed
                self.Reason = 'Directory "{0}" exists'.format(dirname)
            else:
                self.Result = tester.ResultType.Failed
                self.Reason = 'Directory "{0}" exists and it should not'.format(
                    dirname)
        else:
            if self.Value:
                self.Result = tester.ResultType.Failed
                self.Reason = 'Directory "{0}" does not exists and it should'.format(
                    dirname)
            else:
                self.Result = tester.ResultType.Passed
                self.Reason = 'Directory "{0}" does not exists'.format(dirname)
        host.WriteVerbose(["testers.directory", "testers"], "{0} - ".format(
            tester.ResultType.to_color_string(self.Result)), self.Reason)
