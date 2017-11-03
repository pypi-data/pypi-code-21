from __future__ import absolute_import, division, print_function

import os
import copy

import autest.common.is_a as is_a
import autest.testers as testers
import autest.glb as glb
import hosts.output as host

from .runable import Runable
from .order import Order
from .item import Item
from autest.common.constructor import call_base, smart_init
from autest.common.execfile import execFile
from . import setup
from . import conditions
from . import testrun
from . import CopyLogic


@smart_init
class Test(Runable, Order, Item):
    __slots__ = ["__run_serial",
                 "__setup",
                 "__test_runs",
                 "__test_dir",
                 "__test_file",
                 "__test_root",
                 "__run_dir",
                 "__result",
                 "__processes",
                 "__conditions", ]

    @call_base(Runable=(None,), Order=(), Item=(None, "id"))
    def __init__(self, id, test_dir, test_file, run_root, test_root, env, variables):
        self.__run_serial = False

        # internal data
        # the different test runs
        self.__test_runs = []
        # this is the location of the test file
        self.__test_dir = test_dir
        # this is the name of the test file
        self.__test_file = test_file
        # this is the directory we scanned to find this test
        self.__test_root = test_root
        # this is the directory we will run the test in
        self.__run_dir = os.path.normpath(os.path.join(run_root, id))
        # this is the result of the test ( did it pass, fail, etc...)
        self.__result = None
        # controls is we should continue on a failure
        self.__continueonfail = False

        # this is a bit of a hack as this hard coded in..  try to address later
        # this is the set of extra processes that we might need running
        # for the test to work
        # self.__processes=Processes(self)

        # property objects
        self.__setup = setup.Setup(self)
        self.__conditions = conditions.Conditions()

        # make a copy of the environment so we can modify it without issue
        self.Env = env
        # add some default values
        self.Env['AUTEST_TEST_ROOT_DIR'] = self.__test_root
        self.Env['AUTEST_TEST_DIR'] = self.__test_dir
        self.Env['AUTEST_RUN_DIR'] = self.__run_dir
        # additional variables
        self.Variables = variables

# public properties
    @property
    def Name(self):
        return self._ID

    @Name.setter
    def Name(self, val):
        self._ID = val

    @property
    def Summary(self):
        return self._Description

    @Summary.setter
    def Summary(self, val):
        self._Description = val

    @property
    def RunSerial(self):
        return self.__run_serial

    @RunSerial.setter
    def RunSerial(self, val):
        self.__run_serial = val

    @property
    def Setup(self):
        return self.__setup

    def SkipIf(self, *lst):
        return self.__conditions._AddConditionIf(lst)

    def SkipUnless(self, *lst):
        return self.__conditions._AddConditionUnless(lst)

    @property
    def TestDirectory(self):
        return self.__test_dir

    @property
    def TestFile(self):
        return self.__test_file

    @property
    def TestRoot(self):
        return self.__test_root

    @property
    def RunDirectory(self):
        return self.__run_dir

    # public methods
    def AddTestRun(self, name='general', displaystr=None):
        tmp = testrun.TestRun(self, "%s-%s" %
                              (len(self._TestRuns), name), displaystr)
        self._TestRuns.append(tmp)
        return tmp

    # internal stuff

    @property
    def _TestRuns(self):
        return self.__test_runs

    @property
    def _Conditions(self):
        return self.__conditions

    @property
    def _ChildRunables(self):
        return self.Setup._Items + list(self.Processes._Items) + self.__test_runs

    @property
    def ContinueOnFail(self):
        return self.__continueonfail

    @ContinueOnFail.setter
    def ContinueOnFail(self, val):
        self.__continueonfail = val


def loadTest(test):
    # load the test data.  this mean exec the data
    # create the locals we want to pass
    locals = copy.copy(glb.Locals)

    locals.update({
        'test': test,  # backwards compat
        'Test': test,
        'Setup': test.Setup,
        'Condition': conditions.ConditionFactory(test.ComposeVariables(), test.ComposeEnv()),
        'Testers': testers,
        # break these out of tester space
        # to make it easier to right a test
        'Any': testers.Any,
        'All': testers.All,
        'Not': testers.Not,
        'When': glb.When(),
        'CopyLogic': CopyLogic,
    })

    # get full path
    fileName = os.path.join(test.TestDirectory,
                            test.TestFile)
    host.WriteVerbose(["test_logic", "reading"],
                      'reading test "{0}"'.format(test.Name))
    execFile(fileName, locals, locals)
    host.WriteVerbose(["test_logic", "reading"],
                      'Done reading test "{0}"'.format(test.Name))
