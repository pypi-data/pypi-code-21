# pylint: disable=locally-disabled, protected-access, redefined-builtin
from __future__ import absolute_import, division, print_function

import os
import copy
import time

import hosts.output as host
import autest.glb as glb
from autest.common.constructor import call_base, smart_init
import autest.common.is_a as is_a
from autest.common.execfile import execFile
import autest.testers as testers
from autest.core import conditions
from autest.core import CopyLogic
from autest.core.eventinfo import *
from autest.core.test import loadTest
from autest.core.order import GenerateStartOrderedList, GenerateEndOrderedList
from autest.exceptions.killonfailure import KillOnFailureError

from .runlogic import RunLogic
from .process import Process_RunLogic
from .testrun import TestRun_RunLogic


@smart_init
class Test_RunLogic(RunLogic):
    @call_base()
    def __init__(self):
        self.__running = False  # Are we running
        self.__current_run = None  # current running testrun ( as logic object)
        self.__task_stack = []  # a list of objects
        # current running process if any (started by test)
        self.__running_processes = []
        self.__tr_running_processes = [
        ]  # running processes start by a test run
        self.__running_default = None  # the default running process object
        self.__test = None  # The test object
        self._default = None  # the default process object (info)
        self.__start_time = None  # When did we start running.
        self.__delay_time = None  # when we have to delay start of the test run

    def isRunning(self):
        return self.__running

    def canRunTest(self):
        if not self.__test._Conditions._Passed:
            return False
        return True

    def doStart(self, ev):
        '''
        Start up any processes we might have based on the Deafult being defined
        at the Test level there may not be any processes.
        '''

        # get default process
        self._default = self.__test.Processes.Default
        # order processes
        proc_list = GenerateStartOrderedList(self._default)
        # start processes
        tmp = self.StartOrderedItemsAync(proc_list, Process_RunLogic)
        if len(tmp) and is_a.String(tmp[0]):
            # we had a startup failure
            host.WriteVerbosef("test_logic",
                               "Test {0}: Starting of processes Failed!",
                               self.__test.Name)
            return (True, tmp[0], tmp[1])
        self.__running_processes = tmp
        host.WriteVerbosef("test_logic", "Test {0} Started!", self.__test.Name)

        return (False, "No issues found", "Started!")

    def Start(self, test):
        if self.__running:
            return
        self.__running = True
        self.__test = test
        host.WriteMessagef("Running Test {0}:", self.__test.Name, end="")
        host.WriteVerbosef("test_logic", "Starting Test \"{0}\"",
                           self.__test.Name)
        # Make sandbox directory for the given test
        host.WriteVerbosef("test_logic",
                           "Creating sandbox directory for Test {0}",
                           self.__test.Name)
        os.makedirs(self.__test.RunDirectory)
        # read the test
        try:
            loadTest(self.__test)
        except:
            # fill in error case....
            raise

        # validate conditions
        if self.canRunTest():
            # map some events
            self.__test._RegisterEvent(
                "starting_logic",
                self.__test.StartingEvent,
                testers.Lambda(
                    self.doStart,
                    description_group="Starting Test {0}".format(
                        self.__test.Name)))

            # bind events
            self.__test.Setup._BindEvents()
            self.__test._BindEvents()
            # setup event
            self.__test.SetupEvent(SetupInfo())
            # test that everything setup correctly so we can continue
            if self.__test.Setup._Result != testers.ResultType.Passed and self.__test.Setup._Result != testers.ResultType.Warning:
                host.WriteVerbosef("test_logic", "Setup failed for Test {0}",
                                   self.__test.Name)
                return False

            # starting event
            self.__start_time = time.time()
            self.__test.StartingEvent(StartingInfo())
            # started event
            self.__test.StartedEvent(StartedInfo())
        else:
            # cannot run test..  report as needed that this being skipped
            reason = self.__test._Conditions._Reason
            self.__test._Result = testers.ResultType.Skipped
            self.__running = False

            host.WriteMessagef(
                " {0}",
                testers.ResultType.to_color_string(self.__test._Result))
            host.WriteWarning(
                "Skipping test {0} because:\n {1}".format(self.__test.Name,
                                                          reason),
                show_stack=False)
            # clean up any mess
            # such as remove the sandbox if had no issues
            # self.cleanupTest()
        # set the test run we need to process as stack
        self.__task_stack = self.__test._TestRuns[:]

        return True

    def Stop(self):
        if self.__current_run:
            # stop current run
            self.__current_run.Stop()
        # stop all processes
        self.StopItems(self.__running_processes + self.__tr_running_processes)
        self.Poll()
        self.__running = False

    def startTestRun(self):
        # start item
        self.__current_run = TestRun_RunLogic.Run(self.__task_stack[0])
        # map any processes that are defined by the test, but are started by
        # the test run
        self.__tr_running_processes += self.__current_run.TestProcesses
        # pop off first item
        self.__task_stack = self.__task_stack[1:]
        self.__delay_time = None

    def Poll(self):
        while not self.__running:
            return False

        skip = False
        hard_stop = False
        # get test runs
        ret = False
        stack_len = len(self.__task_stack)

        if self.__delay_time:
            if time.time() - self.__delay_time > self.__task_stack[
                    0].DelayStart:
                self.startTestRun()
            ret = True
        elif self.__current_run is None and stack_len:
            # we don't have a anything running start up first item on list
            # check for DelayStart
            if self.__task_stack[0].DelayStart and self.__delay_time is None:
                host.WriteVerbosef(["test_logic"],
                                   "Delaying start of test run {0} by {1} sec",
                                   self.__task_stack[0].Name,
                                   self.__task_stack[0].DelayStart)
                self.__delay_time = time.time()
            else:
                self.startTestRun()
            ret = True
        elif self.__current_run and self.__current_run.Poll(
        ):  # are we still running
            # poll running processes
            try:
                # we don't care is the processes are running or not
                # we just need to trigger the run event on these objects
                self.PollItems(self.__running_processes)
                # call running event on this test object
                self.__test.RunningEvent(
                    RunningInfo(self.__start_time, time.time(),RunlogicWrapper(self)))
            except KillOnFailureError:
                # if we catch this here .. whole test has to stop
                # stop current run
                self.__current_run.Stop()
                skip = True
                hard_stop = True
                # next poll will get the shutdown logic run

            ret = True
        elif self.__current_run:

            # remove and processes started by a test run and are not running
            # anymore
            stopped_processes = [
                x for x in self.__tr_running_processes if not x.isRunning()
            ]
            self.__tr_running_processes = [
                x for x in self.__tr_running_processes if x.isRunning()
            ]
            # for the stopped processes we need make sure they finish
            for p in stopped_processes:
                # simple poll call will make sure it calls any events and cleanup code
                # if it has not happened yet
                p.Poll()

            host.WriteVerbosef(["test_logic"], "Finished test run: {0}",
                               self.__current_run.TestRun.Name)
            # start up next item if we have any
            curr_result = self.__current_run.TestRun._Result
            if curr_result == testers.ResultType.Failed:
                host.WriteMessagef("F", end="")
            elif curr_result == testers.ResultType.Warning:
                host.WriteMessagef("W", end="")
            elif curr_result == testers.ResultType.Exception:
                host.WriteMessagef("E", end="")
            else:
                host.WriteMessagef(".", end="")

            if curr_result != testers.ResultType.Passed and \
                    curr_result != testers.ResultType.Warning:
                # test to see if the test is setup to continue on a failure
                if not self.__current_run.TestRun.ContinueOnFail and not self.__test.ContinueOnFail:
                    skip = True

            # do we have another item to run
            if stack_len:
                # are we skipping tests if we have a failure
                if skip:
                    host.WriteVerbosef(["test_logic"],
                                       "Skipping rest of the test: {0}",
                                       self.__test.Name)
                    # skip test
                    while len(self.__task_stack) != 0:
                        tmp = self.__task_stack[0]
                        tmp._Result = testers.ResultType.Skipped
                        tmp._Reason = "Test run {0} failed".format(
                            self.__current_run.TestRun.Name)
                        self.__task_stack = self.__task_stack[1:]
                    ret = False
                else:
                    # start next test
                    if self.__task_stack[
                            0].DelayStart and self.__delay_time is None:
                        host.WriteVerbosef(
                            ["test_logic"],
                            "Delaying start of test run {0} by {1} sec",
                            self.__task_stack[0].Name,
                            self.__task_stack[0].DelayStart)
                        self.__delay_time = time.time()
                    else:
                        self.startTestRun()
                    ret = True

        if ret is False:
            # all the test runs are done
            # Stop processes
            host.WriteVerbosef(['test_logic'],
                               "Stopping processes owned by Test")
            if hard_stop:
                self.StopItems(self.__running_processes +
                               self.__tr_running_processes)
            else:
                self.StopItems(
                    self.__running_processes + self.__tr_running_processes,
                    self.__test.ComposeVariables().Autest.StopProcessLongDelaySeconds,
                    self.__test.ComposeVariables().Autest.StopProcessShortDelaySeconds)
            # call finished event
            if self.__start_time:
                self.__test.FinishedEvent(
                    FinishedInfo(time.time() - self.__start_time))
            else:
                self.__test.FinishedEvent(FinishedInfo(0))

            # call cleanup event
            self.__test.CleanupEvent(CleanupInfo())

            # output some info
            host.WriteMessagef(
                " {0}",
                testers.ResultType.to_color_string(self.__test._Result))
            if self.__current_run and self.__current_run.TestRun._Result == testers.ResultType.Exception:
                host.WriteWarning(
                    'Stopping test run for test "{0}" because test run "{1}" had an Exception:\n {2}'.
                    format(self.__test.Name, self.__current_run.TestRun.Name,
                           self.__current_run.TestRun._ExceptionMessage))

            self.__running = False
        return ret
