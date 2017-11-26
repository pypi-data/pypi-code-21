'''
Test the reactive queue.  There may be a close issue.

Created on Nov 23, 2017

@author: aevans
'''

from reactive.structures.proc_queue import ReactiveMutliProcessingQueue
import multiprocessing
import sys


class TestReactiveQueue():

    def get_ctx_type(self):
        """
        Get the context type using the platform

        :return:  The context type
        :rtype:  str
        """
        platform = sys.platform
        if platform == "linux" or platform == "linux2":
            self.ctx = multiprocessing.get_context("fork")
        else:
            self.ctx  = multiprocessing.get_context("spawn")

    def test_creation(self):
        ctx = multiprocessing.get_context(self.get_ctx_type())
        rq = ReactiveMutliProcessingQueue(
            maxsize=1000, ctx=ctx)
        rq.put_all([1])
        assert rq.qsize() == 1
        val = rq.get_n_nowait(1)
        assert len(val) is 1
        assert val[0] == 1
        assert rq.qsize() == 0
        rq.close()

    def test_clear_queue(self):
        ctx = multiprocessing.get_context(self.get_ctx_type())
        rq = ReactiveMutliProcessingQueue(
            maxsize=1000, ctx=ctx)
        tst = [x for x in range(0, 1000)]
        rq.put_all(tst)
        assert rq.qsize() == 1000
        rq.clear_queue()
        assert rq.qsize() == 0
        rq.close()
