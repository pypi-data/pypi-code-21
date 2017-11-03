from __future__ import absolute_import, division, print_function
import hosts.output as host
from autest.common.constructor import call_base, smart_init
from autest.core.testenity import TestEnity
import autest.testers as testers
from .process import Process


@smart_init
class Processes(TestEnity):

    @call_base(TestEnity=("runable", ))
    def __init__(self, runable):

        self.__processes = {}
        # this the process we will be viewed as the primary process for the
        # test run
        # if not set we will use try to start the correct based on the
        # order logic
        self.__default = None

    def _Dict(self):
        return self.__processes

    @property
    def _Items(self):
        return self.__processes.values()

    def Process(
            self,
            name,
            cmdstr=None,
            returncode=None,
            startup_timeout=10,  # default to 10 second as most things should be ready by this time
    ):
        # todo ... add check to make sure id a varaible safe

        # create Process object
        tmp = Process(self._Runable, name, cmdstr)

        # set some global settings before the user might override these locally
        tmp.ForceUseShell = self._Runable.ComposeVariables().Autest.ForceUseShell

        # update setting based on values passed in
        if returncode is not None:
            tmp.ReturnCode = returncode

        tmp.StartupTimeout = startup_timeout

        if name in self.__processes:
            host.WriteWarning("Overriding process object {0}".format(name))
        self.__processes[name] = tmp
        self.__dict__[name] = tmp
        return tmp

    # def Add(self, process):
    #     if self.process.Name in self.__processes:
    #         host.WriteWarning("Overriding process object {0}".format(
    #             self.process.Name))
    #     self.__processes[self.process.Name] = self.process
    #     self.__dict__[self.process.Name] = self.process

    @property
    def Default(self):
        if self.__default is None:
            self.__default = self.Process("Default")
            self.__processes["default"] = self.__default
        return self.__default


import autest.api
from autest.core.test import Test
from autest.core.testrun import TestRun
autest.api.AddTestEnityMember(Processes, classes=[Test, TestRun])
