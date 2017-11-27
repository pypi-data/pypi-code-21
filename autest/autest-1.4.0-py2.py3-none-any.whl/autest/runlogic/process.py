# pylint: disable=locally-disabled, protected-access
from __future__ import absolute_import, division, print_function
import os
import sys
import string
import subprocess
import time
import shlex
import traceback

import hosts.output as host

from autest.common.constructor import call_base, smart_init
import autest.common.is_a as is_a
import autest.common.process
from .runlogic import RunLogic
import autest.core.streamwriter as streamwriter
import autest.core.eventinfo as eventinfo
import autest.testers as testers
from autest.exceptions.killonfailure import KillOnFailureError


@smart_init
class Process_RunLogic(RunLogic):

    @call_base()
    def __init__(self):
        self._process = None
        self.__proc = None
        self.__output = None
        self.__stdout = None
        self.__stderr = None

        self.__call_cleanup = True

        self.__start_time = None
        self.__last_event_time = None
        # used to help detect if we are taking to long to get ready
        # ie we don't want the isReady test, be it bound to the process
        # or bound as a function of Process A waiting on Process B
        # to take to long else we could deadlock, if the test is never ready
        self.__startup_time = None
        self.__startup_timeout = None

    def hasRunFor(self, t):
        # Test to see if we have run so long
        runtime = time.time() - self.__start_time
        host.WriteDebugf(
            ["process"],
            "Checking if time passed has been {0} seconds: ran for {1} sec", t,
            runtime)
        return runtime >= t

    def ListCmd(self, cmdstr):
        # hacky function to help deal with command that need a shell without
        # breaking older test files
        lex = shlex.shlex(cmdstr, posix=True)
        if sys.platform =='win32':
            lex.escape="" # normal escape of "\" breaks path passing
        lex.wordchars += '-$%><&.=:%^/\\'
        lex.commenters = ''
        return list(lex)

    def isShellCommand(self, cmdstr):

        # some command characters that suggest we wanted to run in a shell
        core_operators = ';&><|'
        shell_args = [
            ';',
            '&&',
            '&',
            '>',
            '>>',
            '<',
            '|',
            '||',
            'cd',
            'set',
            'export',
        ]
        if os.name == 'nt':
            # extra stuff for windows.. not complete, but common stuff
            shell_args = [
                'echo', 'dir', 'del', 'rmdir', 'rd', 'move', 'rename', 'mkdir'
            ]
        for arg in self.ListCmd(cmdstr):
            if arg.lower() in shell_args:
                return True
            # check the arg does not quoted as a string
            # and that it does not contain a core operator
            # allow us to get cases such as 1>&2 like cases
            if arg[0] not in ['"\'']:
                for o in core_operators:
                    if o in arg:
                        return True
        return False

    def doSetup(self, ev):
        host.WriteVerbosef("testrun_logic", "Setup Test {0}",
                           self._process.Name)
        try:
            self._process.Setup._do_setup()
        except:
            return (True, "Running setup tasks", traceback.format_exc())
        return (False, "Running setup tasks", "Setup succeeded")

    def doStart(self):
        if self.isRunning():
            # in case we are already running
            return
        host.WriteVerbosef(['process'], 'Start process {0}',
                           self._process.Name)
        # so we know we can call clean up once to get the end events testers
        self.__call_cleanup = True

        # setup command line.. do number of subsutions etc..
        command_line = self._process.RawCommand

        # substitute the value of the string via the template engine
        # as this provide a safe cross platform $subst model.
        env = self._process.ComposeEnv(
        )  # get the correct shell env for the process
        template = string.Template(command_line)
        command_line = template.substitute(env)
        # test to see that this might need a shell
        try:
            if self._process.ForceUseShell:
                shell = True
            else:
                shell = self.isShellCommand(command_line)

        except ValueError as e:
            self.__output = streamwriter.StreamWriter(
                self._process.StreamOutputDirectory, command_line, env)
            self.Cleanup()
            raise KillOnFailureError('Bad command line - {0}\n Details: {1}'.
                                     format(command_line, e))
        args = self.ListCmd(command_line) if not shell else command_line

        # call event that we are starting to run the process
        host.WriteDebugf(
            ["process"],
            "Calling StartingRun event with {0} callbacks mapped to it",
            len(self._process.StartingEvent))
        self._process.StartingEvent(eventinfo.StartingInfo())

        host.WriteVerbosef(
            ["process"],
            "Running command:\n '{0}'\n in directory='{1}'\n Path={2}",
            command_line, self._process._RootRunable.RunDirectory, env['PATH'])
        host.WriteDebugf(["process"],
                         "Passing arguments to subprocess as: {0}", args)
        if is_a.List(args):
            finalcmd = subprocess.list2cmdline(args)
            host.WriteDebugf(["process"], "subprocess list2cmdline = {0}",
                             finalcmd)
        else:
            finalcmd = args
        # create a StreamWriter which will write out the stream data of the run
        # to sorted files, as well as make script files of the command ( might
        # break this up later)
        self.__output = streamwriter.StreamWriter(
            self._process.StreamOutputDirectory, finalcmd, env)

        try:
            self.__proc = autest.common.process.Popen(
                args,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self._process._RootRunable.RunDirectory,
                env=env)
        except IOError as err:
            self.Cleanup()
            raise KillOnFailureError('Bad command line - {0}\n Details: {1}'.
                                     format(command_line, err))
        except OSError as err:
            self.Cleanup()
            raise KillOnFailureError('Bad command line - {0}\n Details: {1}'.
                                     format(command_line, err))

        # map pipes for output
        self.__stdout = streamwriter.PipeRedirector(self.__proc.stdout,
                                                    self.__output.WriteStdOut)
        self.__stderr = streamwriter.PipeRedirector(self.__proc.stderr,
                                                    self.__output.WriteStdErr)

        # Get times
        self.__start_time = time.time()
        self.__last_event_time = self.__start_time

        # set event that process was started
        host.WriteDebugf(
            ["process"],
            "Calling RunStarted event with {0} callbacks mapped to it",
            len(self._process.StartedEvent))
        self._process.StartedEvent(eventinfo.StartedInfo)
        self._process._isRunning(True)

    def Cleanup(self):
        if self.__call_cleanup:
            self._process._isRunning(False)
            self.__call_cleanup = False
            if self.__proc is None:
                if self.__output is None:
                    self.__output = streamwriter.StreamWriter(
                        self._process.StreamOutputDirectory,
                        self._process.RawCommand, self._process.ComposeEnv())

                event_info = eventinfo.ProcessFinishedInfo(0, None,
                                                           self.__output)
            else:
                event_info = eventinfo.ProcessFinishedInfo(
                    time.time() - self.__start_time, self.__proc.returncode,
                    self.__output)
                self.__proc = None

            if self.__output:
                self.__output.Close()
                self.__output = None
            if self.__stdout:
                self.__stdout.close()
                self.__stdout = None
            if self.__stderr:
                self.__stderr.close()
                self.__stderr = None

            # call event
            host.WriteDebug(
                ["process"],
                "Calling FinishedEvent event with {0} callbacks mapped to it".
                format(len(self._process.FinishedEvent)))
            self._process.FinishedEvent(event_info)

    def Start(self, process):
        self._process = process

        # bind events
        self._process.Setup._BindEvents()
        self._process._BindEvents()
        # setup event
        self._process.SetupEvent(eventinfo.SetupInfo())
        # test that everything setup correctly so we can continue
        if self._process.Setup._Result != testers.ResultType.Passed and self._process.Setup._Result != testers.ResultType.Warning:
            host.WriteVerbosef("test_logic", "Setup failed for Test {0}",
                               self._process.Name)
            return False
        # For process this will call the rest of the events as needed
        try:
            self.doStart()
        except KillOnFailureError as e:
            self._process._Result = testers.ResultType.Failed
            self._process._Reason = str(e)
            # raise
            return False
        return True

    def Poll(self):
        if self.isRunning():
            curr_time = time.time()
            if curr_time - self.__last_event_time > .5:
                # make event info object
                event_info = eventinfo.RunningInfo(self.__start_time,
                                                   curr_time,
                                                   eventinfo.RunlogicWrapper(self)
                                                   )
                # call event
                try:
                    self._process.RunningEvent(event_info)
                except KillOnFailureError:
                    self.Stop()
                self.__last_event_time = curr_time
            return True
        # We are not running
        # do we need to clean up
        self.Cleanup()
        return False

    def isRunning(self):
        return self.__proc is not None and self.__proc.poll() is None

    def Stop(self):
        host.WriteVerbosef(['process'], 'Stopping process {0}',
                           self._process.Name)
        if self.isRunning():
            self.__proc.killtree(
                self._process.ComposeVariables().Autest.KillDelaySecond)
        self.Cleanup()

    def Wait(self, timeout):
        return self.__proc.waitTimeOut(timeout)

    @property
    def pid(self):
        return self.__proc.pid
