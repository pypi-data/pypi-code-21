# coding=utf-8
""" All the classes and functions that make sshreader tick
"""
# Copyright (C) 2015-2017 Jesse Almanrode
#
#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Lesser General Public License as published by
#     the Free Software Foundation, either version 3 of the License, or
#     (at your option) any later version.
#
#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Lesser General Public License for more details.
#
#     You should have received a copy of the GNU Lesser General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.
from __future__ import absolute_import, print_function, division
from builtins import range  # Replaces xrange in Python2
from collections import namedtuple
from progressbar import ProgressBar
from sshreader.ssh import SSH
from subprocess import Popen, PIPE, STDOUT
from types import FunctionType
import logging
import multiprocessing
import os
import paramiko
import sys
import threading
import time


__author__ = 'Jesse Almanrode (jesse@almanrode.com)'

__cpuHardLimitFactor__ = 3
_printlock_ = multiprocessing.Lock()
logger = logging.getLogger('sshreader')


# Globals
Command = namedtuple('Command', ['cmd', 'stdout', 'stderr', 'return_code'])


def shell_command(command, combine=False, decodebytes=True):
    """Run a command in the shell on localhost and return the output

    :param command: String containing the shell script to run
    :param combine: Direct stderr to stdout
    :param decodebytes: Decode bytes objects to unicode strings
    :return: NamedTuple for (cmd, stdout, stderr) or (cmd, stdout)
    """
    if combine:
        pipeout = Popen(command, shell=True, stdout=PIPE, stderr=STDOUT)
        stdout, stderr = pipeout.communicate()
        assert stderr is None
        if decodebytes:
            result = Command(cmd=command, stdout=stdout.decode().strip(), stderr=None, return_code=pipeout.returncode)
        else:
            result = Command(cmd=command, stdout=stdout.strip(), stderr=None, return_code=pipeout.returncode)
    else:
        pipeout = Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
        stdout, stderr = pipeout.communicate()
        if decodebytes:
            result = Command(cmd=command, stdout=stdout.decode().strip(), stderr=stderr.decode().strip(),
                             return_code=pipeout.returncode)
        else:
            result = Command(cmd=command, stdout=stdout.strip(), stderr=stderr.strip(), return_code=pipeout.returncode)
    return result


class Hook(object):
    """ Custom class for pre and post hooks

    :param target: Function to call when using the hook
    :param args: List of args to pass to target
    :param kwargs: Dictionary of kwargs to pass to target
    :param ssh_established: Should the ssh connection be established when the hook is run
    :return: Hook
    :raises: TypeError
    """

    def __init__(self, target, args=None, kwargs=None, ssh_established=False):
        assert isinstance(target, FunctionType)
        self.target = target
        self.ssh_established = ssh_established
        if args is None:
            self.args = list()
        else:
            assert isinstance(args, list)
            self.args = args
        if kwargs is None:
            self.kwargs = dict()
        else:
            assert isinstance(kwargs, dict)
            self.kwargs = kwargs
        self.result = None

    def run(self, *args, **kwargs):
        """ Run the Hook.  You can add additional args or kwargs at this time!

        :param args: Append to args
        :param kwargs: Append to/update kwargs
        :return: Result from target function
        """
        args = self.args + list(args)
        kwargs = dict(list(self.kwargs.items()) + list(kwargs.items()))
        self.result = self.target(*args, **kwargs)
        return self.result

    def __str__(self):
        return self.__dict__


class ServerJob(object):
    """ Custom class for holding all the info needed to run ssh commands or shell commands in sub-processes or threads

    :param fqdn: Fully qualified domain name or IP address
    :param cmds: List of commands to run (in the order you want them run)
    :param username: Username for SSH
    :param password: Password for SSH
    :param keyfile: Path to ssh key (can be used instead of password)
    :param keypass: Password for private ssh key file
    :param timeout: Tuple of timeouts in seconds (sshtimeout, cmdtimeout)
    :param runlocal: Run job on localhost (skips ssh to localhost)
    :param prehook: Optional Hook object
    :param posthook: Optional Hook object
    :param combine_output: Combine stdout and stderr
    :return: ServerJob Object
    :raises: ValueError, TypeError

    :property results: List of namedtuples (cmd, stdout, stderr, return_code) or (cmd, stdout, return_code)
    :property status: Sum of return codes for entire job (255 = ssh did not connect)
    """
    def __init__(self, fqdn, cmds, username=None, password=None, keyfile=None, keypass=None, timeout=(30, 30),
                 runlocal=False, prehook=None, posthook=None, combine_output=False):
        self.name = fqdn
        self.results = list()
        self.username = username
        self.password = password
        self.key = keyfile
        self.keypass = keypass
        self.status = 0
        self.combine_output = combine_output
        self.runlocal = runlocal
        if isinstance(cmds, (list, tuple)):
            self.cmds = cmds
        else:
            self.cmds = [cmds]
        if isinstance(timeout, (tuple, list)):
            if len(timeout) != 2:
                raise ValueError('You must supply two timeouts if you pass a tuple or list')
            self.sshtimeout = timeout[0]
            self.cmdtimeout = timeout[1]
        else:
            self.sshtimeout = timeout
            self.cmdtimeout = timeout
        if prehook is not None:
            if isinstance(prehook, Hook):
                self.prehook = prehook
            else:
                raise TypeError('prehook should be of type: ' + str(Hook))
        else:
            self.prehook = prehook
        if posthook is not None:
            if isinstance(posthook, Hook):
                self.posthook = posthook
            else:
                raise TypeError('posthook should be of type: ' + str(Hook))
        else:
            self.posthook = posthook
        if runlocal:
            self._conn = "localhost"
        elif not keyfile and not all([username, password]):
            raise paramiko.SSHException("You must enter a username and password or supply an SSH key")

    def run(self):
        """Run a ServerJob. SSH to server, run cmds, return result

        :return: ServerJob.status
        """
        logger.info(str(self.name) + u': Starting')
        if self.runlocal:
            if self.prehook:
                logger.debug(str(self.name) + u':Running prehook')
                self.prehook.run(self)
            for cmd in self.cmds:
                logger.debug(str(self.name) + u': ' + str(cmd))
                result = shell_command(cmd, combine=self.combine_output)
                self.results.append(result)
                logger.debug(str(self.name) + u': ' + str(cmd) + u': ' + str(result))
                self.status += result.return_code
            if self.posthook:
                logger.debug(str(self.name) + u':Running posthook')
                self.posthook.run(self)
        else:
            if self.prehook and self.prehook.ssh_established is False:
                logger.debug(str(self.name) + u':Running prehook')
                self.prehook.run(self)
            try:
                self._conn = SSH(self.name, username=self.username, password=self.password, keyfile=self.key,
                                 timeout=self.sshtimeout)
            except Exception as errorMsg:
                logger.debug(str(errorMsg))
                self.status = 255
                self.results.append(str(errorMsg))
            else:
                if self.prehook and self.prehook.ssh_established:
                    logger.debug(str(self.name) + u':Running prehook')
                    self.prehook.run(self)
                for cmd in self.cmds:
                    logger.debug(str(self.name) + u': ' + str(cmd))
                    result = self._conn.ssh_command(cmd, timeout=self.cmdtimeout, combine=self.combine_output)
                    self.results.append(result)
                    logger.debug(str(self.name) + u': ' + str(cmd) + u': ' + str(result))
                    self.status += result.return_code
                if self.posthook and self.posthook.ssh_established:
                    logger.debug(str(self.name) + u':Running posthook')
                    self.posthook.run(self)
                self._conn.close()
                self._conn = None  # So the ssh connection can be pickled!
            if self.posthook and self.posthook.ssh_established is False:
                logger.debug(str(self.name) + u':Running posthook')
                self.posthook.run(self)
        logger.info(str(self.name) + u': Finished')
        return self.status

    def __str__(self):
        return self.__dict__

    def __getitem__(self, item):
        return self.__dict__[item]


def cpusoftlimit():
    """ Return the default number of sub-processes your system is allowed to spawn

    :return: Integer
    """
    cpu_count = multiprocessing.cpu_count()
    if cpu_count > 1:
        return cpu_count - 1
    else:
        return cpu_count


def cpuhardlimit():
    """ Return the maximum number of sub-processes your system is allowed to spawn.

    cpusoftlimit() * __cpuHardLimitFactor__

    :return: Integer
    """
    global __cpuHardLimitFactor__
    assert isinstance(__cpuHardLimitFactor__, int)
    return cpusoftlimit() * __cpuHardLimitFactor__


def threadlimit():
    """ Return the maximum number of threads each process is allowed to spawn.  The idea here is to not overload a system.

    cpu_count() * 2

    :return: Integer
    """
    return multiprocessing.cpu_count() * 2


def echo(*args, **kwargs):
    """ Wrapper for print that implements a multiprocessing.Lock object as well as uses unbuffered output
    to sys.stdout.

    :param args: Passthrough to print function
    :param kwargs: Passthrough to print function
    :return: None
    """
    global _printlock_
    with _printlock_:
        print(*args, **kwargs)
        sys.stdout.flush()
    return None


def sshread(serverjobs, pcount=None, tcount=None, progress_bar=False):
    """Takes a list of ServerJob objects and puts them into threads/sub-processes and runs them

    :param serverjobs: List of ServerJob objects (A list of 1 job is acceptable)
    :param pcount: Number of sub-processes to spawn (None = off, 0 = cpusoftlimit, -1 = cpuhardlimit)
    :param tcount: Number of threads to spawn (None = off, 0 = threadlimit)
    :param progress_bar: Print a progress bar
    :return: List with completed ServerJob objects (single object returned if 1 job was passed)
    :raises: ExceedCPULimit, TypeError, ValueError
    """
    if tcount is None and pcount is None:
        raise ValueError('Specify an integer for pcount or tcount')
    if isinstance(serverjobs, list):
        islist = True
    else:
        islist = False
        serverjobs = [serverjobs]
    totaljobs = len(serverjobs)

    if logging.getLogger('sshreader').getEffectiveLevel() < 30 and progress_bar:
        logger.info('Logging output enabled. Disabling progress_bar')
        progress_bar = False

    item_counter = multiprocessing.Value('L', 0)
    if progress_bar:
        bar = ProgressBar(max_value=totaljobs)
    else:
        bar = None

    task_queue = multiprocessing.Queue(maxsize=totaljobs)
    result_queue = multiprocessing.Queue(maxsize=totaljobs)

    for job in serverjobs:
        task_queue.put(job)

    if pcount is None:
        # Limit the number of threads to spawn
        if tcount == 0:
            tcount = int(min(totaljobs, threadlimit()))
        else:
            tcount = int(min(tcount, totaljobs))

        logger.info(u"Spawning " + str(tcount) + u" threads")
        # Start a thread pool
        for thread in range(tcount):
            thread = threading.Thread(target=_sub_thread_, args=(task_queue, result_queue, item_counter))
            thread.daemon = True
            thread.start()
    else:
        # Found this while digging around the multiprocessing API.
        # This might help some of the pickling errors when working with ssh
        multiprocessing.allow_connection_pickling()

        # Adjust number of sub-processes to spawn.
        if pcount == 0:
            pcount = cpusoftlimit()
        elif pcount < 0:
            pcount = cpuhardlimit()
        pcount = int(min(pcount, totaljobs))

        if pcount > cpuhardlimit():
            raise ValueError('CPUHardLimit exceeded: ' + str(pcount) + ' > ' + str(cpuhardlimit()))

        if tcount is not None:
            if tcount == 0:
                tcount = int(min(totaljobs // pcount, threadlimit()))
            if tcount < 2:
                # If we don't have enough jobs to spawn more than 1 thread per process, then we won't spawn threads
                tcount = None

        logger.info(u"Spawning " + str(pcount) + u" sub-processes")
        for pid in range(pcount):
            pid = multiprocessing.Process(target=_sub_process_, args=(task_queue, result_queue, item_counter),
                                          kwargs={'thread_count': tcount})
            pid.daemon = True
            pid.start()

    # Non blocking way to wait for threads/processes
    while result_queue.full() is False:
        if progress_bar:
            bar.update(item_counter.value)
        time.sleep(1)
    if progress_bar:
        bar.finish()

    completed_jobs = list()
    while result_queue.empty() is False:
        completed_jobs.append(result_queue.get())

    # If we were passed a list then we will return a list
    if islist:
        return completed_jobs
    else:
        return completed_jobs.pop()


def _sub_process_(task_queue, result_queue, item_counter, thread_count=None):
    """ Private method for managing multi-processing and spawning thread pools.

    DO NOT USE THIS METHOD!
    """
    pid = os.getpid()
    logger.debug(u"Starting process: " + str(pid))
    if thread_count is None:
        while task_queue.empty() is False:
            job = task_queue.get()
            job.run()
            result_queue.put(job)
            with item_counter.get_lock():
                item_counter.value += 1
    else:
        logger.debug(u"Process: " + str(pid) + u" spawning: " + str(thread_count) + u" threads")
        for thread in range(thread_count):
            thread = threading.Thread(target=_sub_thread_, args=(task_queue, result_queue, item_counter))
            thread.daemon = True
            thread.start()
        while threading.active_count() > 1:
            time.sleep(1)
    logger.debug(u"Exiting process: " + str(pid))
    return None


def _sub_thread_(task_queue, result_queue, item_counter):
    """ Private method for managing multi-processing and spawning thread pools.

    DO NOT USE THIS METHOD!
    """
    logger.debug('Entering new thread')
    while task_queue.empty() is False:
        job = task_queue.get()
        job.run()
        result_queue.put(job)
        with item_counter.get_lock():
            item_counter.value += 1
    logger.debug('Exiting thread')
    return None
