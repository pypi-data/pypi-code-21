from __future__ import absolute_import, division, print_function
import hosts.output as host
from . import tester
from autest.exceptions.killonfailure import KillOnFailureError


class _Container(tester.Tester):

    def __init__(self, *lst, **kw):
        self.__testers = lst
        return super(_Container, self).__init__(None, None, **kw)

    def _verify(self, converter):
        tmp = []
        for i in self._testers:
            if isinstance(i, _Container):
                i._verify(converter)
                tmp.append(i)
            elif isinstance(i, tester.Tester):
                tmp.append(i)
            else:
                tmp.append(converter(i))
        self.__testers = tmp

    @property
    def _testers(self):
        return self.__testers

    @property
    def isContainer(self):
        return True

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
        for t in self._testers:
            t.TestValue = self._test_value

    #@property
    # def KillOnFailure( self ):
    #    return self.__kill

    #@KillOnFailure.setter
    # def KillOnFailure( self, value ):
    #    self.__kill = value

    @property
    def Description(self):
        '''
        decription of what is being tested
        '''
        return self._description

    @Description.setter
    def Description(self, val):
        self._description = val
        for t in self._testers:
            t.Description = self._description

    @property
    def DescriptionGroup(self):
        '''
        decription of what is being tested
        '''
        return self._description_group

    @DescriptionGroup.setter
    def DescriptionGroup(self, val):
        self._description_group = val
        for t in self._testers:
            t.DescriptionGroup = self._description_group


class Any(_Container):

    def __init__(self, *lst):
        super(Any, self).__init__(
            *lst, description="Checking that any test passes")

    def test(self, eventinfo, **kw):
        for t in self._testers:
            t.test(eventinfo, **kw)
            if t.Result == tester.ResultType.Passed:
                self.Result = tester.ResultType.Passed
        if self.Result == tester.ResultType.Passed:
            self.Reason = "One or more tests passed"
        else:
            self.Reason = "None of the tests passed"


class All(_Container):

    def __init__(self, *lst):
        super(All, self).__init__(
            *lst, description="Checking that all tests pass")

    def test(self, eventinfo, **kw):
        for t in self._testers:
            t.test(eventinfo, **kw)
            if t.Result == tester.ResultType.Failed:
                self.Result = tester.ResultType.Failed
        if self.Result != tester.ResultType.Failed:
            self.Result = tester.ResultType.Passed

        if self.Result == tester.ResultType.Passed:
            self.Reason = "All the tests passed"
        else:
            self.Reason = "One or more tests did not pass"


class Not(_Container):

    def __init__(self, tester):
        super(Not, self).__init__(
            tester, description="Checking that negation of the test")

    def test(self, eventinfo, **kw):
        t = self._testers[0]        
        try:
            t.test(eventinfo, **kw)
        except KillOnFailureError:
            self.Result = tester.ResultType.Passed
            self.Reason = "The test contained test failed as expected"
            raise
        if t.Result == tester.ResultType.Failed:
            self.Result = tester.ResultType.Passed
            self.Reason = "The test contained test failed as expected"
        # if Warning is clarified better, we might want it to be an error as
        # well
        elif t.Result == tester.ResultType.Passed:
            self.Reason = "The test contained test passed when it was expected to fail"
            self.Result = tester.ResultType.Failed
