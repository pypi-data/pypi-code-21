'''
Test the balancing source.

Created on Nov 17, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem
from reactive.streams.objects.balancing_source import BalancingSource
from test.modules.streams.stream_source import StringSource
from reactive.message.stream_messages import SetPublisher, Pull, Push,\
    SetMaxBatchRequestSize
import time
from test.modules.streams.source import StringTestSource


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()

class TestBalancingSource():

    def stest_creation(self, asys):
        sactor = asys.createActor(StringSource)
        actor = asys.createActor(BalancingSource)
        msg = SetPublisher(sactor, None, None)
        asys.tell(actor, msg)

    def test_pull(self, asys):
        dt = time.time()
        sactor = asys.createActor(StringTestSource)
        src = asys.createActor(BalancingSource)
        msg = SetPublisher(sactor, None, None)
        bsize = SetMaxBatchRequestSize(100, None, None)
        asys.tell(src, msg)
        asys.tell(src, bsize)
        dt = time.time() - dt
        dt = time.time()
        msg = Pull(100, src, None)
        run = True
        i = 0
        while run:
            i += 1
            rval = asys.ask(src, msg)
            assert isinstance(rval, Push)
            assert isinstance(rval.payload, list)
            run = len(rval.payload) == 0

        i= 0
        while i < 10:
            rval = asys.ask(src, msg)
            assert isinstance(rval, Push)
            assert isinstance(rval.payload, list)
            if len(rval.payload) > 0:
                i += 1
                assert len(rval.payload) == 100
                for res in rval.payload:
                    assert isinstance(res, str)
                    assert "Pull" in res
