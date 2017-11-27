from __future__ import absolute_import, division, print_function

import os
import sys
from fnmatch import fnmatch
import time
import shutil
import json

import hosts.output as host
import autest.glb as glb
import autest.common.execfile as execfile
import autest.api as api
from . import setupitem
from . import runtesttask
import autest.testers.tester as testers
from autest.common.disk import remove_read_only
from . import report
from . import test
from autest.runlogic.test import Test_RunLogic
from autest.exceptions.setuperror import SetupError
import autest.testers as testers
from autest.core import conditions
from autest.core import CopyLogic
from .test import loadTest


class Engine(object):
    """description of class"""

    def __init__(self, dump_report=False, env=None, variables=None):
        self.__tests = {}                                                           # the dict of the different tests we have {name:testobj}
        self.__ENV = env
        self.__variables = variables

        self.__test_dir = variables.Autest.TestDir or './'                         # this the root directory to look for the tests
        self.__run_dir = os.path.abspath(variables.Autest.RunDir or './_sandbox')  # this is the directory to run the tests in

        # any special autest directory to look up.  None uses standard one
        self.__autest_site = variables.Autest.Autest_site
        self.__filters = variables.Autest.Filters or '*'                           # which set of tests to run
        self.__action = variables.Autest.Action or 'default'

        self.__command = {
            'run': self.__run,
            'list': self.__list
        }

        # setup the thread pool to run all the tasks
        # if jobs > 1:
        # self.__pool = ThreadPool(jobs)

        # set the engine to be easy to access
        if glb.Engine:
            raise RuntimeError("Only one engine can be created at a time")
        glb.Engine = self

    def Start(self):
        # load setup items
        import autest.setupitems
        # load testrun items
        import autest.testenities
        # load when items
        import autest.whenitem
        # load built in reporter object
        import autest.reporters
        # load condition tests
        import autest.conditions

        if self.__action in self.__command:
            return self.__command[self.__action]()
        else:   # throw error since command is not valid for whatever reason
            raise SetupError("Command {0} is not valid.".format(self.__action))

    def _load_extensions(self):
        # avoid import issues
        from autest.testenities.file import File
        # load files of our extension type in the directory

        # Which directory to use
        if self.__autest_site is None:
            # this is the default
            path = os.path.join(self.__test_dir, 'autest-site')
            # hack to deal with backward compatiblity
            old_path = os.path.join(self.__test_dir, 'gtest-site')
            if not os.path.exists(path) and os.path.exists(old_path):
                host.WriteWarning(
                    "Depracated gest-site found!\n Please rename to autest-site")
                path = os.path.join(self.__test_dir, 'gtest-site')
        else:
            # This is a custom location
            path = os.path.abspath(self.__autest_site)

        # add expected API function so they can be called
        _locals = {
            'RegisterFileType': api.RegisterFileType,
            'AddTestRunSet': api.ExtendTest,  # backward compat
            'ExtendTest': api.ExtendTest,
            'ExtendTestRun': api.ExtendTestRun,
            'AddSetupTask': api.AddSetupItem,  # backward compat
            'AddSetupItem': api.AddSetupItem,
            'AddTester': api.AddTester,
            'SetupTask': setupitem.SetupItem,  # backward compat
            'SetupItem': setupitem.SetupItem,
            'AddTestRunMember': api.AddTestEnityMember,  # backward compat
            'AddTestEnityMember': api.AddTestEnityMember,
            'ExtendCondition': api.ExtendCondition,
            'AddWhenFunction': api.AddWhenFunction,
            'AddMethodToInstance': api.AddMethodToInstance,
            'AuTestVersion': api.AuTestVersion,
            'AUTEST_SITE_PATH': path,
            'SetupError': SetupError,
            # make it easy to define extension
            'Condition': conditions.ConditionFactory(self.__variables, self.__ENV),
            'Testers': testers,
            'Tester': testers.Tester,
            # break these out of tester space
            # to make it easier to right a test
            'Any': testers.Any,
            'All': testers.All,
            'Not': testers.Not,
            'When': glb.When(),
            'File': File,
            "host": host,
            "CopyLogic": CopyLogic,
        }

        old_path = sys.path[:]
        sys.path.append(path)

        # given it exists we want to load data from it
        if os.path.exists(path):
            host.WriteVerbose("engine",
                              "Loading Extensions from {0}".format(path))
            for f in os.listdir(path):
                f = os.path.join(path, f)
                if os.path.isfile(f) and f.endswith("test.ext"):
                    execfile.execFile(f, _locals, _locals)
        elif self.__autest_site is not None:
            host.WriteError(
                "Custom autest-site path note found. Looking for:\n {0}".
                format(path))
        else:
            host.WriteVerbose("engine", "autest-site path not found")
        sys.path = old_path

    def _scan_for_tests(self):
        # scan for tests in and under the provided test directory
        for root, dirs, files in os.walk(self.__test_dir):
            host.WriteVerbose("test_scan", "Looking for tests in", root)
            # Note because we are using os.walk we get the file name with our
            # directory
            # this mean we have to check for duplicated in names else we will
            # have conflicts
            # ie a test might not run as it was replaced by a test with the
            # same name that
            # was loaded at a later time.
            for f in files:
                if f.endswith('.test.py') or f.endswith(".test"):
                    if f.endswith('.test.py'):
                        name = f[:-len('.test.py')]
                    else:
                        name = f[:-len('.test')]

                    for filter in self.__filters:
                        if not filter.startswith("*"):
                            filter = "*" + filter
                        if fnmatch(os.path.join(root, name), filter):
                            # we have a match, use this test
                            break
                    else:
                        # did not get a match
                        host.WriteVerbose("test_scan", "   Skipping test",
                                          name)
                        continue
                    if name in self.__tests:
                        host.WriteWarning("overiding test", name,
                                          "with test in", root)
                    host.WriteVerbose("test_scan", "   Found test", name)
                    self.__tests[name] = test.Test(
                        name, root, f, self.__run_dir, self.__test_dir,
                        self.__ENV, self.__variables)

    def _run_tests(self):
        if self.__jobs > 1:
            # for t in self.__tests.values():
                # self.__pool.addTask(self.__run_test_task, t)
            # self.__pool.waitCompletion()
            pass
        else:
            tmp = list(self.__tests.keys())
            tmp.sort()
            for t in tmp:
                self.__run_test_task(self.__tests[t])

    def __run_test_task(self, task):
        runtesttask.RunTestTask(task, Test_RunLogic, self.__clean)()

    def _make_report(self):
        info = report.ReportInfo(self.__tests.values())
        host.WriteMessage("\nGenerating Report: --------------")

        for r in self.__reporters:
            func = glb.reporters.get(r)
            if func:
                func(info)
            else:
                host.WriteWarningf("Reported {0} not registered", r)

        # test to see if we have some failures or all failures
        if info.TotalPassCount == 0 and info.TotalTestCount:
            return 10  # everything failed && we had some test
        elif info.TotalNotPassCount:
            return 1  # something failed
        else:
            return 0

    # functions for different commands
    def __run(self):
        self.__jobs = self.__variables.Autest.Run.Jobs or 1                                    # how many jobs to try to run at a given time
        self.__reporters = self.__variables.Autest.Run.Reporters or ['default']
        self.__clean = self.__variables.Autest.Run.Clean or 2

        if os.path.exists(self.__run_dir):
            host.WriteVerbose(
                "engine", "The Sandbox directory exists, will try to remove")
            oldExceptionArgs = None
            while True:
                try:
                    shutil.rmtree(self.__run_dir, onerror=remove_read_only)
                except BaseException as e:
                    if e.args != oldExceptionArgs:
                        # maybe this is Windows issue where antivirus won't let
                        # us remove
                        # some random directory, so we're waiting & retrying
                        oldExceptionArgs = e.args
                        time.sleep(1)
                        continue
                    host.WriteError(
                        ("Unable to remove sandbox directory for clean test run"
                            + "\n Reason: {0}").format(e),
                        show_stack=False)
                    raise
                else:
                    # no exceptions, the directory was wiped
                    break

                host.WriteVerbose("engine", "The Sandbox directory was removed")

        host.WriteVerbose("engine", "Loading Extensions")
        self._load_extensions()

        host.WriteVerbose("engine", "Scanning for tests")
        self._scan_for_tests()
        if not self.__tests:
            host.WriteMessage("No tests found to run")
            host.WriteMessage(
                "If your tests are in a different directory try using --directory=<path with tests>"
            )
            return ""

        host.WriteVerbose("engine", "Running tests")
        self._run_tests()

        host.WriteVerbose("engine", "Making report")
        result = self._make_report()

        return result

    def __list(self):
        host.WriteVerbose("engine", "Scanning for tests")
        self._scan_for_tests()
        if not self.__tests:
            host.WriteMessage("No tests found")
            host.WriteMessage(
                "If your tests are in a different directory try using --directory=<path with tests>"
            )
        else:
            for test in self.__tests.values():
                try:
                    loadTest(test)
                except:
                    pass
            if self.__variables.Autest.List.output_json:
                tests = []

                for test in self.__tests.values():
                    tests.append({"name": test.Name, "description": test.Summary})

                host.WriteMessage(json.dumps(tests))
            else:
                host.WriteMessage("{0}".format("Test Name"))
                host.WriteMessage("-" * 80)
                for name in self.__tests:
                    test = self.__tests[name]

                    # apparently summary was never initialized
                    host.WriteMessage("{0}\t\t{1}".format(test.Name, test.Summary))

        return 0
