from __future__ import absolute_import, division, print_function
import autest.glb as glb
import hosts.output as host
from autest.common.constructor import call_base, smart_init
import autest.common.event as event
import autest.common as common
import autest.common.is_a as is_a
import autest.testers as testers
from autest.core.testerset import TesterSet
from .runable import Runable
from .order import Order
from .item import Item
from . import setup


@smart_init
class TestRun(Order, Item, Runable):

    @call_base(Runable=("testobj",), Order=(), Item=("displaystr", "name"))
    def __init__(self, testobj, name, displaystr):

        self.__test = testobj  # this is the parent test object
        self.__exceptionMessage = ''  # this is a error message given an unknown exeception

        # will want to refactor setup later
        self.__setup = setup.Setup(self)

        # this is the result type of the test run
        self.__result = None

        # controls is we should continue on a failure
        self.__continueonfail = False

        # setup testables
        # util object
        class LamdaEq(object):

            def __init__(self, func):
                self.__func = func

            def __eq__(self, rhs):
                return self.__func() == rhs

            def __ne__(self, rhs):
                return self.__func() != rhs

            def __str__(self):
                return self.__func.__name__

        # StillRunningBefore
        self._Register(
            "Test.Process.StillRunningBefore",
            TesterSet(
                testers.Equal,
                True,
                self.SetupEvent,
                converter=lambda val: LamdaEq(val._isRunningBefore),
            ), "StillRunningBefore"
        )
        # StillRunningAfter
        self._Register(
            "Test.Process.StillRunningAfter",
            TesterSet(
                testers.Equal,
                True,
                self.FinishedEvent,
                converter=lambda val: LamdaEq(val._isRunningAfter),
            ), "StillRunningAfter"
        )
        # NotRunningBefore
        self._Register(
            "Test.Process.NotRunningBefore",
            TesterSet(
                testers.Equal,
                False,
                self.SetupEvent,
                converter=lambda val: LamdaEq(val._isRunningBefore),
            ), "NotRunningBefore"
        )
        # NotRunningAfter
        self._Register(
            "Test.Process.NotRunningAfter",
            TesterSet(
                testers.Equal,
                False,
                self.FinishedEvent,
                converter=lambda val: LamdaEq(val._isRunningAfter),
            ), "NotRunningAfter"
        )

    @property
    def Setup(self):
        return self.__setup

    # attributes of this given test run
    @property
    def Name(self):
        return self._ID

    @property
    def DisplayString(self):
        if self._Description:
            return self._Description
        return self.Name

    @property
    def _ExceptionMessage(self):
        if self._Result == testers.ResultType.Exception and self.__exceptionMessage == "":
            for i in self._Testers:
                if i.Result == testers.ResultType.Exception:
                    self.__exceptionMessage = i.Reason
        return self.__exceptionMessage

    @_ExceptionMessage.setter
    def _ExceptionMessage(self, val):
        self.__exceptionMessage = val

    @property
    def _ChildRunables(self):
        return self.Setup._Items + list(self.Processes._Items)

    @property
    def ContinueOnFail(self):
        return self.__continueonfail

    @ContinueOnFail.setter
    def ContinueOnFail(self, val):
        self.__continueonfail = val

    @property
    def TestDirectory(self):
        return self._RootRunable.TestDirectory

    @property
    def TestFile(self):
        return self._RootRunable.TestFile

    @property
    def TestRoot(self):
        return self._RootRunable.TestRoot

    @property
    def RunDirectory(self):
        return self._RootRunable.RunDirectory
