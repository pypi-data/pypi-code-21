from __future__ import absolute_import, division, print_function
import traceback
import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError





class Lambda(tester.Tester):
    def __init__(self, func, kill_on_failure=False, description_group=None):
        super(Lambda, self).__init__(
            value=func,
            test_value=None,
            kill_on_failure=kill_on_failure,
            description_group=description_group)

    def test(self, eventinfo, **kw):
        # run the test function
        try:
            result, desc, message = self.Value(eventinfo)
        except:
            result, desc, message = (True, "Exception was caught!",
                                     traceback.format_exc())
            self.KillOnFailure = True
        self.Description = desc
        self.Reason = message

        # process results
        if result:
            self.Result = tester.ResultType.Failed
            host.WriteVerbose(["testers.Lambda", "testers"], "{0} - ".format(
                tester.ResultType.to_color_string(self.Result)), self.Reason)
            if self.KillOnFailure:
                raise KillOnFailureError(message)
        else:
            self.Result = tester.ResultType.Passed
        host.WriteVerbose(
            ["testers.Lambda", "testers"],
            "{0} - ".format(tester.ResultType.to_color_string(self.Result)),
            self.Reason)
