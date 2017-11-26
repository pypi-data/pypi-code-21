'''
Standard thread safe queue with ability to get and put multiple items to avoid
a speed impact.

Created on Nov 24, 2017

@author: aevans
'''

from queue import Queue, Full, Empty
from time import time


class ReactiveQueue(Queue):

    def __init__(self, maxsize=0):
        """
        Constructor

        :param maxsize:  Maximum number of elements allowed in queue.
        """
        super().__init__(maxsize)

    def get_n_nowait(self, n):
        """
        Get up to n elements from the queue.  Do not block

        :param n:  The number of elements to get
        :type n:  int
        """
        return self.get_n(n, False)

    def get_n(self, n, block=False, timeout=None):
        """
        Get up to n elements in the queue.

        :param n:  The number of elements to potentially get.
        :type n:  int
        :param block:  Whether to block on the queue
        :type block:  boolean
        :param timeout:  Time to wait for elements or None
        :type timeout:  int
        """
        items = []
        if n > 0:
            with self.not_empty:
                run = self._qsize() > 0
                i = 0
                while run:
                    if block and timeout is None:
                        while not self._qsize():
                            self.not_empty.wait()
                    elif timeout is not None and timeout < 0:
                        raise ValueError(
                            "'timeout' must be a non-negative number")
                    elif timeout is not None and timeout >= 0:
                        endtime = time() + timeout
                        while not self._qsize():
                            remaining = endtime - time()
                            if remaining <= 0.0:
                                raise Empty
                            self.not_empty.wait(remaining)
                    item = self._get()
                    items.append(item)
                    i += 1
                    run = self._qsize() > 0 and i < n
                self.not_full.notify()
        return items

    def put_all_nowait(self, objs):
        """
        Put up to n items in the queue without blocking.
        Return objects not put in.

        :param objs:  The objects to put in the queue
        :type objs:  list
        :return:  Objects not put on queue
        :rtype:  list
        """
        return self.put_all(objs, False)
    
    def put_all(self, objs, block=False, timeout=None):
        """
        Put up to n objs in the queue

        :param objs:  The objects to put in the queue
        :type objs:  list
        :param block:  Whether to block on put
        :type block:  boolean
        :param timeout:  The time to wait for space to open
        :type timeout:  int
        :return:  Objects not put in the queue
        :rtye:  list
        """
        with self.not_full:
            while len(objs) > 0 and self._qsize() < self.maxsize:
                el = objs.pop(0)
                if self.maxsize > 0 and block:
                    if timeout is None:
                        while self._qsize() >= self.maxsize:
                            self.not_full.wait()
                    elif timeout < 0:
                        raise ValueError(
                            "'timeout' must be a non-negative number")
                    elif timeout >= 0:
                        endtime = time() + timeout
                        while self._qsize() >= self.maxsize:
                            remaining = endtime - time()
                            if remaining <= 0.0:
                                raise Full
                            self.not_full.wait(remaining)
                self._put(el)
                self.unfinished_tasks += 1
            self.not_empty.notify()
        return objs
