# Copyright Louis Paternault 2015
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""Set of classes extending the standard :mod:`threading` module."""

import contextlib
import functools
import queue
import threading

class Lock:
    """A lock, with contexts :meth:`thread_safe` and :meth:`thread_unsafe`.
    """

    def __init__(self):
        self._lock = threading.RLock()

    @contextlib.contextmanager
    def thread_unsafe(self):
        """Context marking the inner context as thread unsafe.

        This means that no other thread sharing this lock is run in parallel.
        """
        self._lock.acquire()
        yield
        self._lock.release()

    @contextlib.contextmanager
    def thread_safe(self):
        """Context marking the inner context as thread safe.

        This means that other threads sharing this lock can run in parallel.
        """
        self._lock.release()
        yield
        self._lock.acquire()

@functools.total_ordering
class Task:
    """A task to run, with a priority."""
    # pylint: disable=too-few-public-methods

    def __init__(self, priority, *functions):
        self.priority = priority
        self.functions = functions

    def run(self):
        """Run the (list of) tasks."""
        for function in self.functions:
            function()

    def __eq__(self, other):
        return self.priority == other.priority

    def __lt__(self, other):
        return self.priority < other.priority

    def __str__(self):
        return str(self.functions)

class Pool:
    """A pool of threads.

    Can be used as a context, to create and to start threads when entering the
    context, and waiting for the threads to finish when exiting the context.

    Tasks (as :class:`Task`) may be put into the :attr:`Pool.queue`. They will
    be executed by the different threads running in parallel.
    """
    # pylint: disable=too-few-public-methods

    def __init__(self, workers):
        self.queue = Queue(maxsize=2*workers)
        self._threads = list()
        for __ignored in range(workers):
            self._threads.append(
                threading.Thread(
                    target=self.worker,
                    daemon=True,
                    )
                )

    def __enter__(self):
        for thread in self._threads:
            thread.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        for __ignored in self._threads:
            # Sending "end" signal to threads
            self.queue.put(None)
        self.queue.join()
        for thread in self._threads:
            thread.join()
        return False

    def worker(self):
        """Function called in a thread, running tasks got from the queue."""
        while True:
            with self.queue.get() as task:
                if task is None:
                    return
                else:
                    task()

class Queue(queue.Queue):
    """A subclass of :class:`queue.Queue`, with :meth:`get` as a context."""

    @contextlib.contextmanager
    def get(self):
        """Like :meth:`queue.Queue.get`, but calling :meth:`task_done` at the end of the context."""
        # pylint: disable=arguments-differ
        item = super().get()
        yield item
        self.task_done()
