'''
Extension of the multiprocessing queue too allow for a get and put of multiple
items without constantly acquiring locks.

Created on Nov 24, 2017

@author: aevans
'''

import time
from multiprocessing.reduction import ForkingPickler
from multiprocessing.queues import Queue


class ReactiveMutliProcessingQueue(Queue):

    def __init__(self, maxsize=0, ctx=None):
        super().__init__(maxsize=maxsize,ctx=ctx)

    def get_n(self, n, block=True, timeout=None):
        results = []
        with self._rlock:
            try:
                i = 0
                run = True
                while i < n and run:
                    timeout = 0
                    if block:
                        deadline = time.time() + timeout
                        timeout = deadline - time.time()
                    if timeout >= 0 or self._poll(timeout):
                        res = self._recv_bytes()
                        res = ForkingPickler.loads(res)
                        results.append(res)
                        self._sem.release()
                    else:
                        run = False
                    i += 1
            except Exception as e:
                raise e
        # unserialize the data after having released the lock
        return results

    def get_n_nowait(self,n):
        """
        Get up to n items without waiting
        """
        return self.get_n(n, False)

    def put_all(self, objs, block=True, timeout=None):
        """
        Attempt to put all items in the queue.  If items remain they are
        returned.

        :param objs:  The objects to put in the queue
        :type objs:  list
        :param block:  Whether to block on put
        :type block:  boolean
        :param timeout:  time to wait before put
        :type timeout:  int
        """
        assert not self._closed, "Queue {0!r} has been closed".format(self)
        run = True
        with self._notempty:
            while len(objs) > 0 and run:
                assert not self._closed
                if self._sem.acquire(block, timeout):
                    if self._thread is None:
                        self._start_thread()
                    obj = objs.pop(0)
                    self._buffer.append(obj)
                else:
                    run = False
            self._notempty.notify()
        return objs

    def put_all_nowait(self, objs):
        """
        Put all objects from objs in a queue.

        :param objs:  The objects list
        :type objs:  list
        """
        self.put_all(objs, False)

    def clear_queue(self):
        """
        Clear a queue, call before closing.
        """
        if self.qsize() > 0:
            self.get_n_nowait(self.qsize())

    def close(self):
        """
        Close method with clear queue used
        """
        self.clear_queue()
        Queue.close(self)
        if self._thread:
            Queue.cancel_join_thread(self)
