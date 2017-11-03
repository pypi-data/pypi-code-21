
import hosts.output as host
import re

from . import tester
from .file_callback import FileContentCallback
from autest.exceptions.killonfailure import KillOnFailureError


class ExcludesExpression(tester.Tester):

    def __init__(self, regexp, description, killOnFailure=False, description_group=None, reflags=0):
        if isinstance(regexp, str):
            if reflags:
                regexp = re.compile(regexp, reflags)
            else:
                regexp = re.compile(regexp)
        self._multiline = regexp.flags & re.M

        super(ExcludesExpression, self).__init__(
            value=regexp,
            test_value=None,
            kill_on_failure=killOnFailure,
            description_group=description_group,
            description=description
        )

    def test(self, eventinfo, **kw):
        filename = self._GetContent(eventinfo)
        if filename is None:
            filename = self.TestValue.AbsPath
        result = tester.ResultType.Passed
        try:
            failed = False
            details = []
            # if this is multi-line check
            if self._multiline:
                with open(filename, 'r') as infile:
                    data = infile.read()
                failed = self.Value.search(data)
            else:
                # if this is single expression check each line till match
                with open(filename, 'r') as infile:
                    for cnt, l in enumerate(infile):
                        tmp = self.Value.search(l)
                        if tmp:
                            details += [(cnt + 1, l[:-1])]
                            failed = True
            if failed:
                result = tester.ResultType.Failed
                tmpstr = ""
                if details:
                    tmpstr = "\n  Details:\n"
                    for line, text in details:
                        tmpstr += "    {0} : {1}\n".format(text, line)

                self.Reason = 'Contents of {0} contains expression: "{1}"{2}'.\
                              format(filename, self.Value.pattern, tmpstr)

        except IOError as err:
            result = tester.ResultType.Failed
            self.Reason = 'Cannot read {0}: {1}'.format(filename, err)

        self.Result = result
        if result != tester.ResultType.Passed:
            if self.KillOnFailure:
                raise KillOnFailureError
        else:
            self.Reason = 'Contents of {0} excludes expression'.format(
                filename)
        host.WriteVerbose(["testers.ExcludesExpression", "testers"], "{0} - ".format(
            tester.ResultType.to_color_string(self.Result)), self.Reason)
