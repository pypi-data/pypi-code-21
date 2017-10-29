"""Those things that are core to tests.

This module provides the most fundamental test entities, which include such
things as:

- Tests
- Suites
- Test states

Valid States:
    # Generic states.
    NOT_RUN      Set in Manager.py, also default for step record
    PASS         Set in Manager.py
    FAIL         Set in Manager.py
    SKIPPED      Set in Manager.py only applies to run step
    BUG          Set in Manager.py only applies to run step
    BUG_PASS     Set in Manager.py only applies to run step
    TODO         Set in Manager.py only applies to run step
    EXIT_SUITE   Set in Manager.py
    EXIT_ALL     Set in Manager.py
    USER_STOPPED Set in Manager.py

    # Suite specific states.
    CHILD_FAIL Set in Core.py, only valid when calling getResult on a Suite
    PART_RUN   Set in Core.py, only valid when calling getResult on a Suite

    # Run record states, these states can be reported by a run record but are
    # not valid for an individual step.
    BAD_SETUP          Set in Core.py
    BAD_SUITE_SETUP    Set in Core.py
    BAD_TEARDOWN       Set in Core.py
    BAD_SUITE_TEARDOWN Set in Core.py
"""
from __future__ import print_function


import copy
import os
import textwrap
import time
import weakref
import inspect

from CleverSheep.Prog.Aspects import intelliprop
from CleverSheep.Prog.Enum import Enum

from CleverSheep.Test.Tester import Context
from CleverSheep.Test.Tester import Coordinator
from CleverSheep.Test.Tester import options


class State(object):
    """This class simply serves as a namespace for the state enum"""
    _state_enum = Enum("State")

    # Generic states.
    NOT_RUN = _state_enum("NOT_RUN")
    PASS = _state_enum("PASS")
    FAIL = _state_enum("FAIL")
    EXIT_SUITE = _state_enum("EXIT_SUITE")
    EXIT_ALL = _state_enum("EXIT_ALL")
    USER_STOPPED = _state_enum("USER_STOPPED")

    # Run step specific states.
    SKIPPED = _state_enum("SKIPPED")
    BUG = _state_enum("BUG")
    BUG_PASS = _state_enum("BUG_PASS")
    TODO = _state_enum("TODO")

    # Suite specific states.
    CHILD_FAIL = _state_enum("CHILD_FAIL")
    PART_RUN = _state_enum("PART_RUN")
    BAD_SETUP = _state_enum("BAD_SETUP")
    BAD_SUITE_SETUP = _state_enum("BAD_SUITE_SETUP")
    BAD_TEARDOWN = _state_enum("BAD_TEARDOWN")
    BAD_SUITE_TEARDOWN = _state_enum("BAD_SUITE_TEARDOWN")


# Those states that are not failure states for a step record
SUCCESS_STATES = [State.PASS, State.SKIPPED, State.NOT_RUN, State.TODO,
                  State.BUG, State.BUG_PASS]


def dedentLines(lines):
     return textwrap.dedent("\n".join(lines)).splitlines()


class TestInfo(object):
    """Information about a test function.

    This class supports the ``@test(...)`` decorator that is used by
    CleverSheep to mark test functions. All such marked functions are given
    an attribute called ``cs_test_info``, which is in an instance of this
    class.

    This is most commonly used in test filter functions, as registered by
    `addTestFilter`. When tests are marked using the ``@test`` decorator
    they can be given one or more tags and/or flags.

    Currently this is little more than a struct, except that it provides
    a `__getattr__` that returns ``None`` by default.

    """
    def __init__(self, *args, **kwargs):
        """Constructor:

        :Parameters:
          args
            Non-keyword arguments are interpreted by the test framework.
            Each argument is a string. The supported forms are:

              plat:<platformType>
                The test will only be executed if ``<platformType>`` matches
                `Sys.Platform.platformType`. For example: ``"plat:windows"``.

          kwargs
            Any keyword arguments are simply stored as attributes. So, if
            you decorate a ``test_x`` with ``test(xyz=123)`` then
            ``test_x.cs_test_info.xyz`` will be ``123``.

        """
        self.reserved_cs_flags = {}
        self.cs_flags = {}
        self.cs_tags = {}
        for arg in args:
            if ":" in arg:
                name, value = arg.split(":", 1)
                self.cs_flags[name] = value
            else:
                self.cs_flags[arg] = True

        for name in kwargs:
            if name.startswith("cs_"):
                self.reserved_cs_flags[name[3:]] = kwargs[name]
            else:
                self.cs_tags[name] = kwargs[name]

    def copy(self):
        """Return a (deep) copy of this instance."""
        inst = TestInfo()
        inst.reserved_cs_flags.update(copy.deepcopy(self.reserved_cs_flags))
        inst.cs_flags.update(copy.deepcopy(self.cs_flags))
        inst.cs_tags.update(copy.deepcopy(self.cs_tags))
        return inst

    def __getattr__(self, name):
        """Attribute access:

        Provides read access to test method tags. For example, if you mark a
        test:<py>:

            @test(abc="Hello")

        Then, if ``info`` is the test's `TestInfo` object, ``info.abc`` will
        be ``"Hello"``. If the test does not have ``abc`` set then the result
        is ``None``.

        """
        if name in self.__dict__:
            return self.__dict__.get(name)
        return self.cs_tags.get(name, None)


class StepRecord(object):
    """A single record used to store information about the success or
    otherwise of a test phase.

    A test phase is one of those names defined in Step Names
    """
    def __init__(self, state=State.NOT_RUN):
        self.state = state
        self.exc = None
        self.reported = False

    @property
    def hasFailed(self):
        return self.state not in SUCCESS_STATES

    def __str__(self):
        return "StepRecord: %s" % (self.state)


class StepRecordList(object):
    def __init__(self):
        self.entries = []

    def __iter__(self):
        return iter(self.entries)

    def __len__(self):
        return len(self.entries)


class StepNames(object):
    """Container class for the step name constants

    Note: postCheck is treated the same as the run step in terms of step
    record state.
    """

    SUITE_SET_UP = "suiteSetUp"
    SET_UP = "setUp"
    RUN = "run"
    TEAR_DOWN = "tearDown"
    SUITE_TEAR_DOWN = "suiteTearDown"


class RunRecord(object):
    """A set of records containing all information about a single test's run.

    This stores multiple `StepRecord` instances. The records are stored in a
    dictionary keyed by the names defined in the StepNames class.

    Each of the simple names maps to a single `StepRecord`.

    Each of the list names maps to a list of `StepRecord` instances in
    execution order.
    """

    _simpleNames = [StepNames.SET_UP,
                    StepNames.RUN,
                    StepNames.TEAR_DOWN]
    _listNames = [StepNames.SUITE_SET_UP, StepNames.SUITE_TEAR_DOWN]
    _recordNames = _simpleNames + _listNames
    _runTime = None

    def __init__(self):
        self.runTime = RunRecord._runTime
        self.invalid = False
        self._records = {}
        self.extraInfo = {}

    # LC: I don't know if this is needed, it seems to be something to do with
    # pickle
    def __setstate__(self, state):
        self.invalid = False
        self.__dict__.update(state)

    @classmethod
    def startNewRun(cls):
        cls._runTime = time.time()

    @classmethod
    def finishRun(cls):
        cls._runTime = None

    def addStepRecord(self, name):
        """Add a new phase record to this run record.

        Adds a new `StepRecord` for a test phase, which must be one of those
        defined for a `RunRecord`.

        :Parameters:
          name
            The name for the record. It must be the name of a defined test
            phase.

        :Return:
            The newly added `StepRecord` instance. This will always be a newly
            created instance.

        """
        assert name in RunRecord._recordNames
        record = StepRecord()
        if name in RunRecord._simpleNames:
            assert name not in self._records
            self._records[name] = record
        else:
            if name not in self._records:
                self._records[name] = StepRecordList()
            self._records[name].entries.append(record)
        return record

    @property
    def state(self):
        """Get the state for this run record

        This will return the state of the first step it finds that failed
        going in the order they should be run. If nothing failed the test
        state will be used.

        :return: The state of this run record
        """

        # The Suite Set Up should be in one of NOT_RUN, PASS, FAIL, EXIT_SUITE
        # or EXIT_ALL, it shouldn't be in any of the other states
        for rec in self._records.get(StepNames.SUITE_SET_UP, []):
            # If the suite setup failed report a BAD_SUITE_SETUP
            if rec.state is State.FAIL:
                return State.BAD_SUITE_SETUP

            # If it didn't pass return whatever state it is in
            if rec.state is not State.PASS:
                return rec.state

        # The Set Up should be in one of NOT_RUN, PASS, FAIL, EXIT_SUITE
        # or EXIT_ALL, it shouldn't be in any of the other states
        try:
            rec = self._records[StepNames.SET_UP]
        except KeyError:
            pass
        else:
            # If the setup failed report a BAD_SETUP
            if rec.state is State.FAIL:
                return State.BAD_SETUP

            # If it didn't pass return whatever state it is in
            if rec.state is not State.PASS:
                return rec.state

        # Next check the run entry, this can have more varied states
        try:
            test_rec = self._records[StepNames.RUN]
        except KeyError:
            pass
        else:
            # If the test is in a success state check the teardown
            if test_rec.state in SUCCESS_STATES:

                # The Tear Down should be in one of NOT_RUN, PASS, FAIL,
                # EXIT_SUITE or EXIT_ALL, it shouldn't be in any of the other
                # states
                try:
                    rec = self._records[StepNames.TEAR_DOWN]
                except KeyError:
                    pass
                else:
                    # If the tear down failed report a BAD_TEARDOWN
                    if rec.state is State.FAIL:
                        return State.BAD_TEARDOWN

                    # If it didn't pass return whatever state it is in
                    if rec.state is not State.PASS:
                        return rec.state

                # The Suite Tear Down should be in one of NOT_RUN, PASS, FAIL,
                # EXIT_SUITE or EXIT_ALL, it shouldn't be in any of the other
                # states
                for rec in self._records.get(StepNames.SUITE_TEAR_DOWN, []):
                    # If the suite tear down failed report a BAD_SUITE_TEARDOWN
                    if rec.state is State.FAIL:
                        return State.BAD_SUITE_TEARDOWN

                    # If it didn't pass return whatever state it is in
                    if rec.state is not State.PASS:
                        return rec.state

            # If the test is not in a success state or the test was fine and so
            # was the teardown return the test state
            return test_rec.state

        # Default state is not run, the only way to get here should be if there
        # are no records
        return State.NOT_RUN

    @property
    def hasFailed(self):
        for name in self._recordNames:
            try:
                record = self._records[name]
            except KeyError:
                continue

            if name in self._simpleNames:
                if record.state not in SUCCESS_STATES:
                    return True
            else:
                for rec in record.entries:
                    if rec.state not in SUCCESS_STATES:
                        return True

        return False

    def getStepRecord(self, phase):
        """Get the record details for a phase.
        For simple name entries the record is returned.
        For list entries the first failing record is returned or the first
        record.

        :param phase: The phase to get a step record for, should be in
                      StepNames
        :return: The found record or None
        """
        ent = self._records.get(phase, None)

        if ent is not None and phase in self._listNames:
            seq = ent.entries
            for ent in seq:
                if ent.hasFailed:
                    return ent

            return seq[0]

        return ent


class TestItem(object):
    """Base class for `Test` and `Suite` classes.

    """
    def __init__(self, item, uid, parentUid, context, namespace=None):
        """Constructor:

        :Parameters:
          item
            The concrete test item. For a test function/method this is the
            function/method itself. For a `ClassSuite` this is the instance and
            for a `ModuleSuite` this is the the module instance.

          uid
            The unique ID for this item, which is a tuple of strings.

          parentUid
            The unique ID of the parent item or ``None``. Only the root `Suite`
            of a test tree has a parent of ``None``.

          namespace
            A dictionary that provides the containing namespace for the test
            item.

        """
        self.item = item
        self.uid = uid
        self.context = context
        self.parentUid = parentUid
        self.namespace = self._getNamespace(namespace)
        self._collection = None
        self._running = False
        self._marks = {}
        self.extraInfo = {}

    def setMark(self, mark):
        self._marks[mark] = None

    def clearMark(self, mark):
        if mark in self._marks:
            del self._marks[mark]

    def isMarked(self, mark):
        return mark in self._marks

    def setCollection(self, collection):
        self._collection = weakref.proxy(collection)

    @intelliprop
    def level(self):
        """This item's level in the test tree.

        This is the number of ancestors this item has. If zero then this is
        the 'root' item.

        """
        return len(self.ancestors)

    @intelliprop
    def parent(self):
        """The parent of this item, which may be ``None``.

        If this is ``None`` then this item is the root of a (possibly nested)
        suite of tests.

        """
        return self._collection.parent(self)

    @intelliprop
    def ancestors(self):
        """A list of all ancestors for this item.

        Each entry is a UID. The first entry is the oldest ancesctor and the
        last entry is the immediate parent's UID.

        """
        return self._collection.getAncestors(self)

    def hasFailingAncestor(self):
        """Check if any ancestor is considered to have failed.

        An ancestor suite has failed if, for example, its ``suiteSetup``
        failed.

        :Return:
            ``True`` if any ancestors has failed.

        """
        parent = self.parent
        if parent is None:
            return
        # TODO: Temporarily disabled.
        return
        return parent.hasFailed or parent.hasFailingAncestor()

    def _getNamespace(self, namespace=None):
        return namespace or dict([(n, getattr(self.item, n))
            for n in dir(self.item)])

    @intelliprop
    def rawDoc(self):
        """The raw docstring, no cleaning up performed at all."""
        return self.namespace["__doc__"]

    @intelliprop
    def docLines(self):
        """The docstring as lines.

        This is cleaned up to remove leading and trailing blank lines from
        the summary and details.

        :Return:
            A sequence of (non-nul terminated) lines for the docstring. The
            summary (if present) is separated from the details by a single
            empty line.

        """
        summary, description = self._getDocParts()
        if description:
            return summary + [""] + description
        return summary

    @intelliprop
    def doc(self):
        """The docstring after being cleaned up.

        :Return:
            The cleaned up docstrinc as a multiline string. Leading and
            trailing blank lines are removed and the summary is separated from
            any details by a single blakn line. Common leading whitspace is
            also removed from each line.

        """
        return "\n".join(self.docLines)

    def _getDocParts(self):
        # Lose leading blank lines.
        lines = self.rawDoc.splitlines()
        while lines and not lines[0].strip():
            lines.pop(0)

        # All lines up to next blank line are the summary.
        summary = []
        while lines and lines[0].strip():
            summary.append(lines.pop(0))

        # Strip leading and trailing blank lines from the remaining details.
        while lines and not lines[0].strip():
            lines.pop(0)
        while lines and not lines[-1].strip():
            lines.pop()

        # Dedent the summary and details before returning them.
        summary = summary[:1] + dedentLines(summary[1:])
        details = dedentLines(lines)
        return summary, details

    @property
    def summary(self):
        summary, description = self._getDocParts()
        return " ".join(summary)

    @property
    def details(self):
        summary, description = self._getDocParts()
        return description

    @property
    def sourcesUnderTest(self):
        sources = []
        for p in self.namespace.get("sources_under_test", []):
            if not os.path.isabs(p):
                p = os.path.abspath(os.path.join(self.dirname, p))
            sources.append(p)
        p = self.parent
        if p is not None:
            sources.extend(p.sourcesUnderTest)
        return sources

    @property
    def klass(self):
        return None

    @property
    def path(self):
        p = self.namespace.get("__file__", None)
        if p is None:
            return self.parent.path
        if p.endswith(".pyc"):
            p = p[:-1]
        return p

    @property
    def dirname(self):
        f = self.path
        if f:
            return os.path.dirname(f)

    @property
    def isBug(self):
        return False


class Test(TestItem):
    typeName = "Test"
    isSuite = False
    amNull = False

    def __init__(self, *args, **kwargs):
        super(Test, self).__init__(*args, **kwargs)
        self._runHistory = []
        self.stopAll = False
        if self.func:
            self.func.cs_test_info.test = weakref.proxy(self)

    def getHistory(self):
        return self._runHistory

    def dumpHist(self):
        return self._runHistory[-1].dump()

    def startNewRun(self):
        rec = RunRecord()
        self._runHistory.append(rec)

    def abortRun(self):
        self._runHistory.pop()

    def addStepRecord(self, name):
        runRecord = self._runHistory[-1]
        return runRecord.addStepRecord(name)

    @property
    def postCheck(self):
        return self.parent.postCheck

    @property
    def klass(self):
        return self.parent.klass

    @property
    def funcName(self):
        return self.item.func_name

    @property
    def func(self):
        return self.item

    @property
    def info(self):
        return self.func.cs_test_info

    @property
    def isBroken(self):
        if not hasattr(self, "info"):
            raise AttributeError("%r has no attribute %r" % (
                self.__class__.__name__, "info"))
        flag = self.info.reserved_cs_flags.get("broken", None)
        if flag is None:
            flag = self.info.cs_flags.get("broken", False) # deprecated
        return flag

    @property
    def isTodo(self):
        if not hasattr(self, "info"):
            raise AttributeError("%r has no attribute %r" % (
                self.__class__.__name__, "info"))
        return self.info.cs_flags.get("todo", False)

    @property
    def isBug(self):
        if not hasattr(self, "info"):
            raise AttributeError("%r has no attribute %r" % (
                self.__class__.__name__, "info"))
        flag = self.info.reserved_cs_flags.get("bug", None)
        if flag is None:
            flag = self.info.cs_flags.get("bug", False) # deprecated
        return flag

    @property
    def shouldFork(self):
        if not hasattr(self, "info"):
            raise AttributeError("%r has no attribute %r" % (
                self.__class__.__name__, "info"))
        if self.info.reserved_cs_flags.get("fork", False):
            return True
        parent = self.parent
        try:
            return parent.suite.cs_attrs.fork_all
        except AttributeError:
            return False

    @property
    def testID(self):
        return self.info.cs_tags.get("testID", None)

    @property
    def title(self):
        return self.info.cs_flags.get("title", None)

    @property
    def isRunnable(self):
        if self.parent.exited:
            return False
        return True

    @property
    def state(self):
        rec = self.runRecord
        if rec:
            return rec.state
        return State.NOT_RUN

    @property
    def hasFailed(self):
        rec = self.runRecord
        if rec:
            return rec.hasFailed
        return False

    def addRunRecord(self, record):
        self._runHistory.append(record)
        if len(self._runHistory) > 5:
            self._runHistory[:] = self._runHistory[-5:]

    @property
    def runRecord(self):
        """The XXX TODO"""
        if self._runHistory:
            for rec in reversed(self._runHistory):
                if not rec.invalid:
                    return rec

    def getStepRecord(self, phase):
        return self._runHistory[-1].getStepRecord(phase)

    def getTestProcedure(self):
        return self._collection.spec.getThing(self)


class NullTest(Test):
    amNull = True

    def __init__(self):
        context = Context.getContext(dirPath=os.getcwd())
        super(NullTest, self).__init__(None, None, None, context)
        self.number = 0
        self.startNewRun()

    def startNewRun(self):
        rec = RunRecord()
        self._runHistory.append(rec)

    def abortRun(self):
        self._runHistory.pop()

    @property
    def isBug(self):
        return False

    def __nonzero__(self):
        return False


class Suite(TestItem):
    typeName = "Suite"
    isSuite = True

    def __init__(self, *args, **kwargs):
        self.myDir = kwargs.pop("myDir")
        super(Suite, self).__init__(*args, **kwargs)
        self.exited = False
        self.number = 0
        self.skipTests = False
        self.entered = False

    def reset(self):
        self.entered = False
        self.skipTests = False

    @intelliprop
    def children(self):
        """All the direct children of this item."""
        tests = [t for t in self._collection if t.parent is self]
        suites = [t for t in self._collection.suites if t.parent is self]
        return suites + tests

    @intelliprop
    def tests(self):
        """All the direct test children of this item."""
        return [t for t in self._collection if t.parent is self]

    @property
    def suite(self):
        return self.item

    @property
    def runAfter(self):
        """The _run_after for this source."""
        return self.namespace.get("_run_after", [])

    @property
    def postCheck(self):
        return self.namespace.get("postCheck", lambda: None)

    @property
    def setUp(self):
        return self.namespace.get("setUp", lambda: None)

    @property
    def postSetUp(self):
        return self.namespace.get("postSetUp", lambda: None)

    @property
    def tearDown(self):
        return self.namespace.get("tearDown", lambda: None)

    @property
    def suiteSetUp(self):
        return self.namespace.get("suiteSetUp", lambda: None)

    @property
    def suiteTearDown(self):
        return self.namespace.get("suiteTearDown", lambda: None)

    def getSpecFor(self, name):
        item = self.namespace.get(name, None)
        if item is None:
            return None
        return self._collection.spec.getThing(item)

    def getState(self):
        """Get the overall state of this suite

        :return: The state of the Suite
        """
        run_count = 0
        child_states = []
        return_state = State.PASS
        if not self.children:
            return_state = State.NOT_RUN
            return return_state

        # Build up a list of all unique child states
        for c in self.children:
            state = c.state
            run_count += state is not State.NOT_RUN
            if state not in child_states:
                child_states.append(state)

        # Note while some of these conditions could be collapsed they
        # intentionally have not been, the order is important and it is clearer
        # what happens for each state keeping them separate.
        if State.FAIL in child_states:
            return_state = State.CHILD_FAIL
        elif State.CHILD_FAIL in child_states:
            return_state = State.CHILD_FAIL
        elif State.BAD_SUITE_SETUP in child_states:
            return_state = State.BAD_SUITE_SETUP
        elif State.BAD_SETUP in child_states:
            return_state = State.CHILD_FAIL
        elif State.BAD_TEARDOWN in child_states:
            return_state = State.CHILD_FAIL
        elif State.BAD_SUITE_TEARDOWN in child_states:
            return_state = State.BAD_SUITE_TEARDOWN
        elif State.EXIT_SUITE in child_states:
            return_state = State.EXIT_SUITE
        elif State.EXIT_ALL in child_states:
            return_state = State.EXIT_ALL
        elif State.USER_STOPPED in child_states:
            return_state = State.USER_STOPPED
        elif State.PART_RUN in child_states:
            return_state = State.PART_RUN
        elif State.NOT_RUN in child_states:
            if run_count:
                return_state = State.PART_RUN
            else:
                return_state = State.NOT_RUN

        return return_state

    @property
    def state(self):
        return self.getState()

    def hasTests(self):
        # Deprecated. Only used for old reporter support.
        for t in self._collection:
            if t.parent is self:
                return True


class ModuleSuite(Suite):
    pass


class ClassSuite(Suite):
    @property
    def klass(self):
        return self.item.__class__.__name__
