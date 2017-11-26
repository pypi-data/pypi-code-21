'''
Test the creation and messaging to a subscription.

Created on Nov 2, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem

from reactive.message.stream_messages import Cancel, Push, SetDropPolicy,\
    GetDropPolicy, Peek
from reactive.streams.base_objects.subscription import Subscription
from test.modules.actors import StringBatchTestActor


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestSubscription():

    def test_creation_and_cancel(self, asys):
        sta = asys.createActor(StringBatchTestActor)
        sub = asys.createActor(Subscription)
        cancel = Cancel(None, sub, sub)
        asys.tell(sub, cancel)

    def set_drop_policy(self, asys):
        sta = asys.createActor(StringBatchTestActor)
        sub = asys.createActor(Subscription)
        sdp = SetDropPolicy("pop", sub, sub)
        asys.tell(sub, sdp)
        gdp = GetDropPolicy(None, sub, sub)
        rval = asys.ask(sub, gdp)
        assert isinstance(rval, GetDropPolicy)
        assert rval.payload == "pop"
        cancel = Cancel(None, sub, sub)
        asys.tell(sub, cancel)


    def test_push_pull(self, asys):
        sta = asys.createActor(StringBatchTestActor)
        sub = asys.createActor(Subscription)
        batch = ["a", "b", "c"]
        msg = Push(batch, sub, sub)
        asys.tell(sub, msg)
        msg = Peek(1, sub, None)
        rval = asys.ask(sub, msg)
        assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) == 1
        assert rval.payload[0] == "a"
        cancel = Cancel(None, sub, sub)
        asys.tell(sub, cancel)
