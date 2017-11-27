import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError


class FileContentCallback(tester.Tester):
    '''
    Class that is used to check file contents via some arbitrary function.

    Interface is as follows:

    def callback(data):
        return errorMessage

    where data is file contents (read by this class) and errorMessage is a string describing
    what's wrong with the file; if file is okay return '' or None from the callback

    '''

    def __init__(self, callback, description, killOnFailure=False, description_group=None):
        super(FileContentCallback, self).__init__(value=callback,
                                                  test_value=None,  # set when it add the the tester member, should be a filename
                                                  kill_on_failure=killOnFailure,
                                                  description_group=description_group,
                                                  description=description)

    def test(self, eventinfo, **kw):
        filename = self._GetContent(eventinfo)
        if filename is None:
            filename = self.TestValue.AbsPath
        result = tester.ResultType.Passed
        try:
            with open(filename, 'r') as inp:
                data = inp.read()
        except IOError as err:
            result = tester.ResultType.Failed
            self.Reason = 'Cannot read {0}: {1}'.format(filename, err)
        else:
            # call the callback ( as it is Value)
            errorMessage = self.Value(data)
            if errorMessage:
                result = tester.ResultType.Failed
                self.Reason = 'Contents of {0} do not match desired callback: {1}'.\
                              format(filename, errorMessage)

        self.Result = result
        if result != tester.ResultType.Passed:
            if self.KillOnFailure:
                raise KillOnFailureError
        else:
            self.Reason = 'Contents of {0} match desired callback'.format(
                filename)
        host.WriteVerbose(["testers.Equal", "FileContentCallback"], "{0} - ".format(
            tester.ResultType.to_color_string(self.Result)), self.Reason)
