'''
Created on Nov 5, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem
from reactive.streams.base_objects.subscription_pool import SubscriptionPool
from reactive.message.stream_messages import GetDropPolicy, Cancel
from reactive.actor.base_actor import BaseActor
from reactive.message.router_messages import Subscribe, DeSubscribe
from reactive.message.stream_sub_pool_messages import GetSubscribers


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class SubscriberToTest(BaseActor):
    pass

class TestSubscriptionPool:

    def test_subscription_pool(self, asys):
        sp = asys.createActor(SubscriptionPool)
        gdp = GetDropPolicy(None, sp, None)
        rval = asys.ask(sp, gdp)
        assert isinstance(rval, GetDropPolicy)
        assert rval.payload == "ignore"

    def test_cancel(self, asys):
        sp = asys.createActor(SubscriptionPool)
        cncl = Cancel(None, sp, None)
        asys.tell(sp, cncl)

    def test_subscription(self, asys):
        sp = asys.createActor(SubscriptionPool)
        sub = asys.createActor(SubscriberToTest)
        sm = Subscribe(sub, sp, None)
        asys.tell(sp, sm)
        gs = GetSubscribers(None, sp, None)
        rval = asys.ask(sp, gs)
        assert isinstance(rval, GetSubscribers)
        assert len(rval.payload) == 1
        assert rval.payload[0] == sub
        desub = DeSubscribe(sub, sp, None)
        asys.tell(sp, desub)
        gs = GetSubscribers(None, sp, None)
        rval = asys.ask(sp, gs)
        assert isinstance(rval, GetSubscribers)
        assert len(rval.payload) == 0
        cncl = Cancel(None, sp, None)
        asys.tell(sp, cncl)
