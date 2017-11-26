'''
Test the transient example actor

Created on Nov 22, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem, ActorExitRequest
from test.modules.transient.basic import TransientTestActor
from reactive.message.stream_messages import Push, Pull, TearDown
from test.modules.streams.fake_sub import FakeSub
from reactive.message.stream_work_stage_messages import SetSubscriptionPool
from datetime import datetime
import time


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestTransientActor:

    def test_creation(self, asys):
        actr = asys.createActor(TransientTestActor)
        asys.tell(actr, TearDown(None, actr, None))
        asys.tell(actr, ActorExitRequest())

    def test_work_batch(self, asys):
        actr = asys.createActor(TransientTestActor)
        sub = asys.createActor(FakeSub)
        msg = SetSubscriptionPool(sub, actr, None)
        asys.tell(actr, msg)
        pll = Pull(100, actr, None)
        rval = asys.ask(actr, pll)
        assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) is 0
        run = True
        dt = datetime.now()
        while run and (dt - datetime.now()).total_seconds() < 120:
            rval = asys.ask(actr, actr, None)
            rval = asys.ask(actr, pll)
            assert isinstance(rval, Push)
            assert isinstance(rval.payload, list)
            if len(rval.payload) > 0:
                run = False
        assert len(rval.payload) > 0
        for val in rval.payload:
            assert "Pull" in val
        asys.tell(actr, TearDown(None, actr, None))
        asys.tell(actr, ActorExitRequest())
