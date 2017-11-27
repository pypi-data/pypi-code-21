'''
Module overrides Popen and introduces killtree function
'''

from __future__ import absolute_import, division, print_function

import subprocess
import os
import signal

import ctypes
import time

import hosts.output as host

if os.name == 'nt':
    from . import win32

    def killtree(self, kill_delay=1):
        '''
        Kills a process with all its children

        Current issue... Windows is a message based system. Classic CLI programing generally does not use message pumps.
        By design windows does not use interupts, but instead an event based system. This mean the way 
        CTRL-C is handled is different from that of POSIX like OS systems. In this case Windows dispatched a CTRL-C to 
        all processes in a given console windows. It does not give it to given process. To work around this we can make
        a stub program that can assign itself to a new console windows, dispatch the ctrl-c simutlated event to allow for 
        the POSIX like sig.int logic. Otherwise, windows really was thinking you would send a quit messages and it 
        would shut down before you did a terminate.

        '''

        #host.WriteVerbosef(['process-kill'], "sent signal.CTRL_C_EVENT to process {0}", self.pid)
        #os.kill(self.pid, signal.CTRL_C_EVENT)
        #host.WriteVerbosef(['process-kill'], "waiting up to {0} sec before calling Terminate", kill_delay)
        #if self.waitTimeOut(kill_delay):
            #host.WriteVerbosef(['process-kill'], "Process {0} still running! Calling Terminate!!", self.pid)
            # pylint: disable=locally-disabled, protected-access
            #win32.TerminateJobObject(self._job, -1)
        #else:
        win32.TerminateJobObject(self._job, -1)
            #host.WriteVerbosef(['process-kill'], "Process {0} finished", self.pid)

    def waitTimeOut(process, timeout):
        # WaitForSingleObject expects timeout in milliseconds, so we convert it
        # pylint: disable=locally-disabled, protected-access
        win32.WaitForSingleObject(
            int_to_handle(process._handle), int(timeout * 1000))
        return process.poll() is None

    def int_to_handle(value):
        '''
        Casts Python integer to ctypes.wintypes.HANDLE
        '''
        return ctypes.cast(
            ctypes.pointer(ctypes.c_size_t(value)),
            ctypes.POINTER(ctypes.wintypes.HANDLE)).contents

    # pylint: disable=locally-disabled, protected-access, no-member
    def Popen(*args, **kw):
        '''
        Keep args description in the comment for reference:
        args, bufsize=None, stdin=None, stdout=None, stderr=None,
        preexec_fn=None, close_fds=False, shell=False, cwd=None, env=None,
        universal_newlines=None, startupinfo=None, creationflags=None, **kw
        '''

        job = win32.CreateJobObject(None, "")
        extended_info = win32.JOBOBJECT_EXTENDED_LIMIT_INFORMATION()
        if not win32.QueryInformationJobObject(
                job, win32.JobObjectExtendedLimitInformation,
                ctypes.byref(extended_info),
                ctypes.sizeof(win32.JOBOBJECT_EXTENDED_LIMIT_INFORMATION),
                None):
            raise ctypes.WinError()
        extended_info.BasicLimitInformation.LimitFlags = (
            win32.JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE)
        if not win32.SetInformationJobObject(
                job, win32.JobObjectExtendedLimitInformation,
                ctypes.byref(extended_info),
                ctypes.sizeof(win32.JOBOBJECT_EXTENDED_LIMIT_INFORMATION)):
            raise ctypes.WinError()

        # this is to deal with anything new
        args = list(args)
        kw = dict(kw)
        kw['creationflags'] = kw.get('creationflags',
                                     0) | subprocess.CREATE_NEW_PROCESS_GROUP
        # In the case of windows we want to make a job object for the given
        # process
        # on windows we want to start the process suspended so we can apply job
        # object correctly
        # I have to yet to do this....  so there is a small race that can
        # happen
        process = subprocess.Popen(*args, **kw)

        win32.AssignProcessToJobObject(job, int_to_handle(process._handle))
        process._job = job
        return process
else:

    def killtree(self, kill_delay=1):
        '''
        Terminates a process and all its children
        '''
        # pylint: disable=locally-disabled, no-member
        # try to kill group with a ctrl-C
        pgid = os.getpgid(self.pid)
        host.WriteVerbosef(['process-kill'], "sent signal.SIGINT to process group {0}", pgid)
        os.killpg(pgid, signal.SIGINT)
        host.WriteVerbosef(['process-kill'], "waiting up to {0} sec before sending signal.SIGKILL", kill_delay)
        if self.waitTimeOut(kill_delay):
            host.WriteVerbosef(['process-kill'], "Process group {0} still running! Sending signal.SIGKILL!!", pgid)
            try:
                os.killpg(pgid, signal.SIGKILL)
            except OSError as e:
                # If this a 3 (no such process) error we ignore it
                # mac os will throw permission errors ie value 1
                if e.errno != 3 and e.errno != 1:
                    raise
        else:
            host.WriteVerbosef(['process-kill'], "Process group {0} finished", pgid)

    def waitTimeOut(process, timeout):
        startTime = time.time()
        endTime = startTime + timeout
        while (time.time() < endTime) and (process.poll() is None):
            # This sleep the thread it is called in
            time.sleep(0.1)
        return process.poll() is None

    # pylint: disable=locally-disabled, invalid-name, no-member
    def Popen(*args, **kw):
        '''
        Wraps subprocess.Popen
        '''

        # this is to deal with anything new
        args = list(args)
        kw = dict(kw)
        if 'preexec_fn' in kw:
            preexec_fn = kw['preexec_fn']

            def wrapper(*lst, **kw):
                '''
                Calls setsid before preexec_fn
                '''
                os.setsid()
                return preexec_fn(*lst, **kw)

            kw['preexec_fn'] = wrapper
        else:
            kw['preexec_fn'] = os.setsid
        return subprocess.Popen(*args, **kw)


# add killtree function
subprocess.Popen.killtree = killtree
subprocess.Popen.waitTimeOut = waitTimeOut
