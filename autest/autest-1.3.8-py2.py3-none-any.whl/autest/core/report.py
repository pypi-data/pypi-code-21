'''
Report object that knows how to print itself and can be exported to a file
'''
from __future__ import absolute_import, division, print_function
from autest.testers.tester import ResultType, Tester
import hosts.output as host


class ReportInfo(object):
    ''' class contains information about the tests stats
        and accessors to get the test based on there status
    '''

    def __init__(self, tests):
        # counts...
        self.__stats = {
            0: 0,  # Unknown =0
            1: 0,  # Passed = 1
            2: 0,  # Skipped = 2
            3: 0,  # Warning = 3
            4: 0,  # Failed = 4
            5: 0,  # Exception = 5
        }

        # the tests group by there status
        self.__grouped_tests = {
            100: []  # clean up key.. value is all not passing tests
        }
        self.__tests = tests

        for t in tests:
            # for each test map them based on there state
            self.__stats[t._Result] += 1
            try:
                self.__grouped_tests[t._Result].append(t)
            except KeyError:
                self.__grouped_tests[t._Result] = [t]
            # this is a group of test that did not pass
            # ie it was a warning, or skipped or passed state
            if t._Result in [ResultType.Exception, ResultType.Failed, ResultType.Unknown]:
                self.__grouped_tests[100].append(t)

    @property
    def stats(self):
        return self.__stats

    @property
    def TotalTestCount(self):
        return len(self.__tests)

    @property
    def TotalPassCount(self):
        return self.stats[ResultType.Passed] + self.stats[ResultType.Warning]

    @property
    def TotalNotPassCount(self):
        return self.stats[ResultType.Exception] + \
            self.stats[ResultType.Failed] + \
            self.stats[ResultType.Unknown]

    @property
    def TotalWarningCount(self):
        return self.stats[ResultType.Warning]

    @property
    def TotalErrorCount(self):
        return self.stats[ResultType.Error]

    @property
    def TotalExceptionCount(self):
        return self.stats[ResultType.Exception]

    @property
    def TotalUnknownCount(self):
        return self.stats[ResultType.Unknown]

    @property
    def Unknown(self):
        return self.__grouped_tests.get(ResultType.Unknown, [])

    @property
    def Passed(self):
        return self.__grouped_tests.get(ResultType.Passed, [])

    @property
    def Skipped(self):
        return self.__grouped_tests.get(ResultType.Skipped, [])

    @property
    def Warning(self):
        return self.__grouped_tests.get(ResultType.Warning, [])

    @property
    def Failed(self):
        return self.__grouped_tests.get(ResultType.Failed, [])

    @property
    def Exception(self):
        return self.__grouped_tests.get(ResultType.Exception, [])

    @property
    def NotPassing(self):
        # all tests that are not skipped, warning or passing
        return self.__grouped_tests.get(100, [])

    @property
    def Tests(self):
        return self.__tests
