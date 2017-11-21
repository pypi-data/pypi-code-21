#
# A library to manage ARCFIRE experiments
#
#    Copyright (C) 2017 Nextworks S.r.l.
#    Copyright (C) 2017 imec
#
#    Sander Vrijders   <sander.vrijders@ugent.be>
#    Dimitri Staessens <dimitri.staessens@ugent.be>
#    Vincenzo Maffione <v.maffione@nextworks.it>
#    Marco Capitani    <m.capitani@nextworks.it>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., http://www.fsf.org/about/contact/.
#

import multiprocessing.dummy as multiprocessing
import sys

import rumba.log as log

if sys.version_info[0] >= 3:
    import contextlib
else:
    import contextlib2 as contextlib


logger = log.get_logger(__name__)


def call_in_parallel(name_list, argument_list, executor_list):
    """
    Calls each executor in executor_list with the corresponding
    argument in argument_list

    Assumes that the three lists are the same length, will fail otherwise.
    Is equivalent to
    for i, e in enumerate(executor_list):
        e(argument_list[i])
    but all calls will be executed in parallel.

    If successful, no output will be given. Otherwise, this will raise
    the exception raised by one failed call at random.

    :param name_list: list of names of the executors (used for logging)
    :param argument_list: list of arguments to the executors
    :param executor_list: list of executors (as functions)
    """
    if len(executor_list) != len(name_list) \
            or len(executor_list) != len(argument_list):
        raise ValueError("Names, arguments and executors lists "
                         "must have the same length")

    def job(executor, name, m_queue, argument):
        try:
            # m_queue.cancel_join_thread()
            logger.debug('Starting process "%s".'
                         % (name,))
            executor(argument)
            m_queue.put("DONE")
        except BaseException as e:
            logger.error('Setup failed. %s: %s',
                         type(e).__name__,
                         str(e))
            m_queue.put(e)

    logger.debug('About to start spawning processes.')
    queue = multiprocessing.Queue()
    with contextlib.ExitStack() as stack:
        # This is a composite context manager.
        # After exiting the 'with' block, the __exit__ method of all
        # processes that have been registered will be called.
        msg_to_be_read = 0
        for i, e in enumerate(executor_list):
            stack.enter_context(ProcessContextManager(
                target=job,
                args=(e, name_list[i], queue, argument_list[i])
            ))
            msg_to_be_read += 1
        results = []
        for _ in range(len(executor_list)):
            result = queue.get()  # This blocks until results are available
            msg_to_be_read -= 1
            results.append(result)
        for result in results:
            if result != "DONE":
                raise result
    # If we get here, we got a success for every node, hence we are done.


class ProcessContextManager(object):

    def __init__(self, target, args=None, kwargs=None):
        if args is None:
            args = ()
        if kwargs is None:
            kwargs = {}
        self.process = multiprocessing.Process(
            target=target,
            args=tuple(args),
            kwargs=kwargs
        )

    def __enter__(self):
        self.process.start()
        return self.process

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is not None or exc_val is not None or exc_tb is not None:
            logger.error('Subprocess error: %s.' % (type(exc_val).__name__,))
            try:
                self.process.terminate()
                self.process.join()
            except AttributeError:
                # We are using multiprocessing.dummy, so no termination.
                # We trust the threads will die with the application
                # (since we are shutting down anyway)
                pass
            return False
        else:
            self.process.join()
            return True
