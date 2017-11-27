from __future__ import absolute_import, division, print_function
from autest.common.event import EventInfo
from autest.common.constructor import call_base, smart_init


class SetupInfo(EventInfo):
    def __init__(self):
        pass


class StartingInfo(EventInfo):
    def __init__(self):
        pass


class StartedInfo(EventInfo):
    def __init__(self):
        pass


#proxy object for runnable object to retrict what the user can call
class RunlogicWrapper(object):
    def __init__(self,runlogic):
        self.__runlogic = runlogic

    def isRunning(self):
        return self.__runlogic.isRunning()

    def Stop(self):
        return self.__runlogic.Stop()

    def isProcess(self):
        return self.pid is not None 

    def pid(self):
        try:
            return self.__runlogic.pid
        except:
            return None 


class RunningInfo(EventInfo):
    def __init__(self, start, current, runtime):
        self.startTime = start
        self.currentTime = current
        self.object = runtime
        
        super(RunningInfo, self).__init__()

    @property
    def TotalRunTime(self):
        return self.currentTime - self.startTime


@smart_init
class FinishedInfo(EventInfo):
    @call_base(EventInfo=())
    def __init__(self, runtime):
        self.__runtime = runtime

    @property
    def TotalRunTime(self):
        return self.__runtime


@smart_init
class ProcessFinishedInfo(FinishedInfo):
    @call_base(FinishedInfo=('runtime', ))
    def __init__(self, runtime, returncode, streamwriter):
        self.__returncode = returncode
        self.__runtime = runtime
        self.__all_file = streamwriter.FullFile
        self.__stdout_file = streamwriter.StdOutFile
        self.__stderr_file = streamwriter.StdErrFile
        # self.__message_file=streamwriter.MessageFile
        self.__warning_file = streamwriter.WarningFile
        self.__error_file = streamwriter.ErrorFile
        self.__verbose_file = streamwriter.VerboseFile
        self.__debug_file = streamwriter.DebugFile

    @property
    def ReturnCode(self):
        return self.__returncode

    @property
    def AllFile(self):
        return self.__all_file

    @property
    def StdOutFile(self):
        return self.__stdout_file

    @property
    def StdErrFile(self):
        return self.__stderr_file

    #@property
    #def MessageFile(self):
    #    return self.__message_file

    @property
    def WarningFile(self):
        return self.__warning_file

    @property
    def ErrorFile(self):
        return self.__error_file

    @property
    def VerboseFile(self):
        return self.__verbose_file

    @property
    def DebugFile(self):
        return self.__debug_file


class CleanupInfo(EventInfo):
    def __init__(self):
        pass
