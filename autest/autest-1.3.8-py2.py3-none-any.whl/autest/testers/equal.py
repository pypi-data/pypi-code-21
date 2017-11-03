from __future__ import absolute_import, division, print_function
import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError


class Equal(tester.Tester):

    def __init__(self, value, test_value=None, kill_on_failure=False, description_group=None, description=None):
        if description is None:
            description = "Checking that {0} == {1}"
        super(Equal, self).__init__(value=value,
                                    test_value=test_value,
                                    kill_on_failure=kill_on_failure,
                                    description_group=description_group,
                                    description=description)

    def test(self, eventinfo, **kw):
        # Get value to test against
        val = self._GetContent(eventinfo)
        self.Description = self.Description.format(
            tester.get_name(self.TestValue), self.Value, ev=eventinfo)
        # do test
        if val != self.Value:
            self.Result = tester.ResultType.Failed
            if self.DescriptionGroup:
                self.DescriptionGroup.format(eval=eventinfo)
            reason = "Returned Value {0} != {1}".format(val, self.Value)
            self.Reason = reason
            if self.KillOnFailure:
                raise KillOnFailureError
        else:
            self.Result = tester.ResultType.Passed
            self.Reason = "Returned Value: {0} == {1}".format(val, self.Value)
        host.WriteVerbose(["testers.Equal", "testers"], "{0} - ".format(
            tester.ResultType.to_color_string(self.Result)), self.Reason)
