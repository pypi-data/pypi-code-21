from __future__ import absolute_import, division, print_function
import abc
import traceback
import colorama

from autest.exceptions.killonfailure import KillOnFailureError


def get_name(obj):
    if hasattr(obj, '__call__'):
        return "{0} {1}".format(obj.__self__.Name, obj.__name__)
    return obj


class ResultType(object):
    Unknown = 0
    Skipped = 1
    Passed = 2
    Warning = 3
    Failed = 4
    Exception = 5

    # TODO dynamically generate this? 
    # @classmethod
    # def to_list():
    #     return ["Unknown", "Skipped", "Passed", "Warning", "Failed", "Exception"]

    @classmethod
    def to_string(cls, v):
        for name, value in vars(cls).items():
            if value == v:
                return name
        return "Unknown"

    @classmethod
    def to_color_string(cls, v):
        c = colorama.Style.BRIGHT
        if ResultType.Unknown == v:
            c = colorama.Style.BRIGHT
        elif ResultType.Passed == v:
            c = colorama.Fore.GREEN
        elif ResultType.Skipped == v:
            c = colorama.Style.BRIGHT
        elif ResultType.Warning == v:
            c = colorama.Fore.YELLOW
        elif ResultType.Failed == v:
            c = colorama.Fore.RED
        elif ResultType.Exception == v:
            c = colorama.Fore.RED

        ResultType.to_string(v)
        return colorama.Style.RESET_ALL + c + ResultType.to_string(
            v) + "{{host.reset-stream}}"


class Tester(object):
    '''
    The base tester object contains the basic properties all testers should fill in
    Description - this is what we are testing such as "Tesing return code is 5" or "Checking file file X exists"
    Result - this returns a ResultType object telling us how to process the result of the test
    Reason - this is a string (possibly multiline) with information about why the result happened. This maybe as
    simple as "Return code equal to 5" or it might be more complex with diffs of what was different in a text file
    DescriptionGroup - this is extra information about the file, process, etc that might be useful to give the
    test more context, sould be in form of Type: name, ie Process: proc1
    '''

    def __init__(self,
                 value,
                 test_value,
                 kill_on_failure=False,
                 description_group=None,
                 description=None):
        self._description_group = description_group
        self._description = description
        self.__result = ResultType.Unknown
        self.__reason = "Test was not run"
        self._test_value = test_value
        self.__kill = kill_on_failure
        self.__value = value
        self.__ran = False

    @property
    def KillOnFailure(self):
        '''
        If this is set to True we want to stop that main process
        from running
        '''
        return self.__kill

    @KillOnFailure.setter
    def KillOnFailure(self, value):
        self.__kill = value

    @property
    def TestValue(self):
        '''
        This is the runtime value we want to test against. This
        attribute will return the value in question or a function
        that can get this value for us.
        '''
        return self._test_value

    @TestValue.setter
    def TestValue(self, value):
        self._test_value = value

    @property
    def Value(self):
        '''
        This is the "static" value to test for based on what was set
        in the test file.
        '''
        return self.__value

    @Value.setter
    def Value(self, val):
        self.__value = val

    @property
    def Description(self):
        '''
        decription of what is being tested
        '''
        return self._description

    @Description.setter
    def Description(self, val):
        self._description = val

    @property
    def DescriptionGroup(self):
        '''
        decription of what is being tested
        '''
        return self._description_group

    @DescriptionGroup.setter
    def DescriptionGroup(self, val):
        self._description_group = val

    @property
    def Reason(self):
        '''
        information on why something failed
        '''
        return self.__reason

    @Reason.setter
    def Reason(self, val):
        self.__reason = val

    @property
    def Result(self):
        '''
        Should return True or False based on if the test passed
        '''
        return self.__result

    @Result.setter
    def Result(self, val):
        '''
        Sets the result of a test
        '''
        self.__result = val

    def __call__(self, eventinfo, **kw):
        try:
            self.__ran = True
            self.test(eventinfo, **kw)
        except KeyboardInterrupt:
            raise
        except KillOnFailureError:
            raise
        except:
            self.Result = ResultType.Exception
            self.Reason = traceback.format_exc()

    @abc.abstractmethod
    def test(self, eventinfo, **kw):
        '''
        This is called to test a given event
        it should store the result of the test in the Result property
        and set the message of why the test failed to the ResultData property
        The return value is ignored
        '''
        return

    def _GetContent(self, eventinfo, test_value=None):
        # if test_value is None
        # we set it to the this testers object
        # test value.
        if test_value is None:
            test_value = self.TestValue

        # start off by trying to call this as an object
        # that now how to get content off the event info
        # object.
        try:
            ret, msg = test_value.GetContent(eventinfo)
            if ret is None:
                self.Result = ResultType.Failed
                self.Reason = msg
                return None
            return ret
        except AttributeError:
            pass
        # if that did not work because GetContent() does not exist
        # try to call object as a function (ie callable) that takes
        # that takes an eventinfo object
        try:
            ret, msg = test_value(eventinfo)
            if ret is None:
                self.Result = ResultType.Failed
                self.Reason = msg
                return None
            return ret
        except TypeError:
            pass
        # if that did not work see if this
        # is a string.  If so we assume it an attibute of the event
        if isinstance(test_value, str):
            if not hasattr(eventinfo, test_value):
                self.Result = ResultType.Failed
                self.Reason = "{0} does not have attibute {1}".format(
                    type(eventinfo), test_value)
                return None
            return getattr(eventinfo, test_value)
        # if that failed, we see if this has a __call__ attribute
        # in this case we know we can call it as a function.
        # we assume that it accepts no arguments as we woudl not know
        # what to pass it.
        elif hasattr(test_value, '__call__'):
            return test_value()
        # this is the else
        # we give up and assume it the value we want to pass in
        return test_value

    @property
    def UseInReport(self):
        return True

    @property
    def RanOnce(self):
        return self.__ran

    @property
    def isContainer(self):
        return False
