# pylint: disable=locally-disabled, protected-access
from __future__ import absolute_import, division, print_function
from autest.testers.tester import ResultType, Tester
import hosts.output as host

###################################
# helper functions


def indentStr(str, indent, preindent=None):
    indentstr = " " * indent
    if preindent is None:
        preindent = indentstr
    else:
        preindent = " " * preindent
    if str:
        # add to indent to beginning and replace all \n with \n and extra spaces
        # to prevent \n propagation remove all \n at end and add only one \n
        tmp = preindent + \
            str.replace("\n", "\n" + indentstr).rstrip(" ").rstrip("\n") + "\n"
        return tmp
    return str


###########################################
# header information for a Test


def TestInfo(test, indent=0):
    ret = 'Test: {0}: {3}\n   File: {1}\n   Directory: {2}\n'.format(
        test.Name, test.TestFile, test.TestDirectory,
        ResultType.to_color_string(test._Result))
    if test._Reason:
        ret += "    Reason: {0}\n".format(indentStr(test._Reason, 4, 0))

    return indentStr(ret, indent)


###########################################
# header info about a testrun


def TestRunInfo(tr, indent=0):
    ret = "Run: {0}: {1}\n".format(tr.DisplayString,
                                   ResultType.to_color_string(tr._Result))
    if tr._Reason:
        ret += "   Reason: {0}\n".format(indentStr(tr._Reason, 4, 0))
    return indentStr(ret, indent)


###########################################
# header information for a Process


def ProcessInfo(ps, indent=0):
    if ps._Result == ResultType.Unknown:
        ret = 'Process: {0}: {1}\n'.format(
            ps.Name, ResultType.to_color_string(ResultType.Skipped))
        ps._Reason = "Was not started"
    else:
        ret = 'Process: {0}: {1}\n'.format(
            ps.Name, ResultType.to_color_string(ps._Result))
    if ps._Reason:
        ret += "   Reason: {0}\n".format(indentStr(ps._Reason, 4, 0))
    return indentStr(ret, indent)


###########################################
# Body data for a SetupItem


def SetupItemData(check, indent=0):
    ret = ""
    result = ResultType.to_color_string(check._Result)
    ret = '{0} : {1} - {2}\n'.format("Setting up", check.ItemName, result)

    if check._Result != ResultType.Passed:
        ret += '   Reason: {0}\n'.format(indentStr(check._Reason, 4, 0))

    return indentStr(ret, indent)


###########################################
# Body data for a some check tester


def CheckerData(item, indent=0):
    ret = ""
    if item.Result == ResultType.Passed:
        reason = None
    else:
        reason = item.Reason
    result = ResultType.to_color_string(item.Result)
    ret = '{0} : {1} - {2}\n'.format(
        "{0}".format(item.DescriptionGroup)
        if item.DescriptionGroup is not None else "Test",
        item.Description,
        result,
        indent=" " * indent)
    ret += '   Reason: {0}'.format(indentStr(item.Reason, 4, 0))
    if item.isContainer:
        for tester in item._testers:
            ret += "\n"
            ret += CheckerData(tester, 2)
    ret += "\n"
    return indentStr(ret, indent)


###########################################
# Body data for a Process


def ProcessData(obj, indent=0):

    ret = ProcessInfo(obj)
    if not obj._Reason:
        # print info setup logic
        ret += ReportSetup(obj, 2)
        # dump information about the checks we did for the test run
        ret += ReportCheckers(obj, 2)
    ret += "\n"
    return indentStr(ret, indent)


###########################################
# Body data for a TestRun


def TestRunData(obj, indent=0):
    ret = TestRunInfo(obj, indent)
    if not obj._Reason:
        # print info setup logic
        ret += ReportSetup(obj, 2)

        if obj._Result == ResultType.Passed:
            # don't print anythign extra for passing tests ( until we add some
            # detailed option)
            pass
        elif obj._Result == ResultType.Skipped:
            ret += "  Previous test run failed".format(indent=" " * indent)
        elif obj._Result == ResultType.Exception and obj._ExceptionMessage:
            ret += indentStr(obj._ExceptionMessage, 2)
        else:
            # dump information about the checks we did for the test run
            ret += ReportCheckers(obj, 2)

        # dump info about processes in the testrun
        ret += ReportProcesses(obj, 2)
    ret += "\n"
    return indentStr(ret, indent)


###########################################
# Body data for a Test


def TestData(obj, indent=0):
    ret = ""
    ret += TestInfo(obj, 0)
    if not obj._Reason:
        # print info setup logic
        ret += ReportSetup(obj, 2)
        # print info about any tester at this level
        ret += ReportCheckers(obj, 2)
        # print info about any processes at this level
        ret += ReportProcesses(obj, 2)
        # print info about any TestRuns
        ret += ReportTestRun(obj, 2)

    return indentStr(ret, indent)


def ReportSetup(obj, indent=0):
    ret = ""
    for item in obj.Setup._Items:
        if item.RanOnce:
            ret += SetupItemData(item)
    # if not ret:
    #ret="Nothing to setup\n"
    return indentStr(ret, indent)


def ReportProcesses(obj, indent=0):
    ret = ""
    for p in obj.Processes._Items:
        ret += ProcessData(p)
    # if not ret:
    #ret="No Processes defined\n"
    return indentStr(ret, indent)


def ReportTestRun(obj, indent=0):
    ret = ""
    for tr in obj._TestRuns:
        ret += TestRunData(tr)
    if not ret:
        ret = "No Test run defined\n"
    return indentStr(ret, indent)


def ReportCheckers(obj, indent=0):
    ret = ""
    for check in obj._Testers:
        if check.RanOnce:
            ret += CheckerData(check)
    # if not ret:
    #ret="Nothing was checked\n"

    return indentStr(ret, indent)


def GenerateReport(info, ):  # args):
    '''default ConsoleHost based report'''

    # main report loop
    ####################################
    # report an skipped tests
    if len(info.Skipped) and True:  # args.report_skipped:
        skipped = info.Skipped

        host.WriteMessage("{0} Tests were skipped:".format(len(skipped)))
        host.WriteMessage("-" * 80)
        for test in skipped:
            host.WriteMessage(
                ' Test "{0}" Skipped\n    File: {1}\n    Directory: {2}'.
                format(test.Name, test.TestFile, test.TestDirectory))
            host.WriteMessage("  Reason: {0}".format(test._Conditions._Reason))
            host.WriteMessage()

    #####################################
    # report tests that only had warnings
    if len(info.Warning):
        host.WriteMessage("{0} Tests had warnings:".format(len(skipped)))
        # for test in info.Warning:

    #############################################
    # report tests that had issues (unkown, failed, exceptions)
    tests = info.NotPassing
    indent = 1
    for test in tests:
        ####################################
        # report about the test as a whole
        # print info
        host.WriteMessage(TestData(test, 1))

    # print stats for all tests
    host.WriteMessage('Total of {0} test'.format(info.TotalTestCount))
    for resType in (ResultType.Unknown, ResultType.Exception,
                    ResultType.Failed, ResultType.Warning, ResultType.Skipped,
                    ResultType.Passed):
        amount = info.stats[resType]
        host.WriteMessage('  {0}: {1}'.format(
            ResultType.to_string(resType), amount))


import autest.api as api

api.RegisterReporter(GenerateReport, name="default")
api.RegisterReporter(GenerateReport, name="color-console")
