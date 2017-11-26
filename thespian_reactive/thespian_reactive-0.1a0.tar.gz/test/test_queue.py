'''
Test the standard queue with improvements.

Created on Nov 24, 2017

@author: aevans
'''

from reactive.structures.thread_queue import ReactiveQueue


class TestQueue:

    def test_put(self):
        q = ReactiveQueue(100)
        batch = [x for x in range(0,100)]
        q.put_all(batch)
        assert q.qsize() == 100

    def test_get(self):
        q = ReactiveQueue(100)
        batch = [x for x in range(0,100)]
        q.put_all(batch)
        assert q.qsize() == 100
        q.get_n(100)
        assert q.qsize() == 0
