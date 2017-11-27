from __future__ import absolute_import, division, print_function
import time

import hosts.output as host

from autest.common.constructor import call_base, smart_init
import autest.common.is_a as is_a
from .runlogic import RunLogic
from .process import Process_RunLogic
import autest.testers as testers
from autest.core.order import GenerateStartOrderedList, GenerateEndOrderedList
from autest.core.eventinfo import *
from autest.exceptions.killonfailure import KillOnFailureError



@smart_init
class TestRun_RunLogic(RunLogic):
    # runs a given test

    @call_base()
    def __init__(self):
        self.__running = False
        self.__running_processes = None
        self.__test_processes = []
        self.__running_default = None
        self.__tr = None
        self._default = None
        self.__start_time = 0

    def isRunning(self):
        return self.__running

    def doStart(self, ev):
        # get default process
        self._default = self.__tr.Processes.Default
        # order processes
        proc_list = GenerateStartOrderedList(self._default)
        if len(proc_list) == 0:
            return (
                True, "Generating Process list of processes to start",
                'List came back empty.\n Did you define a process for test run "{0}"'.
                format(self.__tr.DisplayString))
        idx = 0
        for i in proc_list:
            if i.object == self._default:
                break
            idx += 1
        # start processes
        tmp = self.StartOrderedItemsAync(proc_list, Process_RunLogic)

        if is_a.String(tmp[0]):
            # we had a startup failure
            host.WriteVerbosef("testrun_logic",
                               "TestRun {0}: Starting of processes Failed!",
                               self.__tr.Name)
            return (True, tmp[0], tmp[1])
        # get processes that are own by test object and add them to its list of
        # running processes
        self.__test_processes = [
            x for x in tmp if x._process._ParentRunable != self.__tr
        ]
        self.__running_processes = tmp
        self.__running_default = self.__running_processes[idx]
        return (False, "No Issues found", "Started!")

    def Start(self, testrun):
        if self.__running:
            return
        self.__running = True
        self.__tr = testrun

        # map some events
        self.__tr._RegisterEvent(
            "starting_logic",
            self.__tr.StartingEvent,
            testers.Lambda(
                self.doStart,
                kill_on_failure=True,
                description_group="Starting TestRun {0}".format(
                    self.__tr.Name)))

        # bind events
        self.__tr.Setup._BindEvents()
        self.__tr._BindEvents()
        try:
            # setup event
            self.__tr.SetupEvent(SetupInfo())
            # test that everything setup correctly so we can continue
            if self.__tr.Setup._Result != testers.ResultType.Passed and self.__tr.Setup._Result != testers.ResultType.Warning:
                host.WriteVerbosef("test_logic", "Setup failed for Test {0}",
                                   self.__tr.Name)
                return False
            # starting event
            self.__start_time = time.time()
            self.__tr.StartingEvent(StartingInfo())
            # started event
            self.__tr.StartedEvent(StartedInfo())
        except KillOnFailureError:
            # Something went wrong starting up
            # stop everything and allow everything to shutdown
            # for this testrun
            self.Stop()
            self.__running = False
        return True

    def Stop(self):
        for r in self.ShutdownItems(self.__running_processes):
            if not r:
                break
        self.__running = False

    def Poll(self):
        if not self.__running:
            return False
        # wait for default process stop
        if self.__running_default.isRunning():
            self.PollItems(self.__running_processes)
            # call running event
            self.__tr.RunningEvent(RunningInfo(self.__start_time, time.time(),RunlogicWrapper(self)))
            return True

        # call poll to allow all event to go off
        self.__running_default.Poll()
        # get shutdown order
        # get all processes part of this test run
        # these are process we do have to shutdown
        tr_processes = self.__running_processes
        # filter out processes not own by the test run
        tr_processes = [x for x in tr_processes if self.isLocalProcess(x)]

        ####################################################
        # check for all processes to end within a time frame
        if len(tr_processes):
            host.WriteVerbosef(['testrun_logic'],
                               "Stoping processes owned by TestRun")
            self.StopItems(tr_processes, 
            self.__tr.ComposeVariables().Autest.StopProcessLongDelaySeconds,
            self.__tr.ComposeVariables().Autest.StopProcessShortDelaySeconds)

        # call finished event
        if self.__start_time:
            self.__tr.FinishedEvent(
                FinishedInfo(time.time() - self.__start_time))
        else:
            self.__tr.FinishedEvent(FinishedInfo(0))

        # call cleanup event

        self.__running = False
        return False

    @property
    def TestRun(self):
        return self.__tr

    @property
    def TestProcesses(self):
        return self.__test_processes

    def isLocalProcess(self, process):
        return process._process.Name in self.__tr.Processes._Dict()
