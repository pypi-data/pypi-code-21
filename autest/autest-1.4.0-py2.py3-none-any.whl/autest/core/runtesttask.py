from __future__ import absolute_import, division, print_function
import autest.glb as glb
from autest.common.constructor import call_base, smart_init
import hosts.output as host

from autest.common.task import Task
import autest.common.disk as disk
import autest.testers as testers
from autest.exceptions.killonfailure import KillOnFailureError

import os
import traceback
import copy
import time
import shutil


@smart_init
class RunTestTask(Task):

    @call_base(Task=("self",))
    def __init__(self, test, startlogic, clean):
        self.__test = test  # this is the test object
        self.__logic = startlogic  # this the logic start the task with
        self.__clean = clean

    # needed by higher level tasking system.
    def isSerial(self):
        return self.__test.RunSerial

    def __call__(self):
        tl = None
        try:
            tl = self.__logic.Run(self.__test)
        except KillOnFailureError:
            # validate the we did not have a setup error
            self.__test._Result = testers.ResultType.Failed
            host.WriteVerbose("test_logic", "Test {0} failed with KillOnFailureError\n {1}".format(
                self.__test.Name, self.__test.Setup._Reason))

            if self.__test._Result <= self.__clean:
                shutil.rmtree(self.__test.RunDirectory,
                              onerror=disk.remove_read_only)
            return
        except SystemExit as e:
            self.__test._Result = testers.ResultType.Exception
            self.__test._Reason = str(e)
            host.WriteVerbose("test_logic", "Test {0} failed with Exception\n {1}".format(
                self.__test.Name, self.__test._Reason))
            if tl:
                tl.Stop()

            if self.__test._Result <= self.__clean:
                shutil.rmtree(self.__test.RunDirectory,
                              onerror=disk.remove_read_only)
            return
        except Exception as e:
            self.__test._Result = testers.ResultType.Exception
            self.__test._Reason = traceback.format_exc()
            host.WriteVerbose("test_logic", "Test {0} failed with Exception\n {1}".format(
                self.__test.Name, self.__test._Reason))
            if tl:
                tl.Stop()

            if self.__test._Result <= self.__clean:
                shutil.rmtree(self.__test.RunDirectory,
                              onerror=disk.remove_read_only)
            return

        try:
            while tl.Poll():
                time.sleep(.1)

            if self.__test._Result <= self.__clean:
                shutil.rmtree(self.__test.RunDirectory,
                              onerror=disk.remove_read_only)
        except KeyboardInterrupt:
            # ctrl-c was pushed ( or soft term)
            tl.Stop()
            raise
        except:
            # something bad happen try not to hang
            tl.Stop()
            raise
