'''
A troupe supervisor test.

Created on Nov 24, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem, ActorExitRequest
from reactive.streams.objects.troupe_stage_supervisor import TroupeStageSupervisor
from reactive.message.stream_messages import TearDown, SetPublisher, Pull, Push,\
    RegisterKlass
from reactive.streams.objects.transient_stage_supervisor import TransientStageSupervisor
from reactive.streams.base_objects.round_robin_subscription_pool import RoundRobinSubscriptionPool
from reactive.message.stream_work_stage_messages import SetSubscriptionPool
from test.modules.base_object_actors import PublisherRandActor
from reactive.message.router_messages import Subscribe
from test.modules.troupes.basic import TroupeTestActor
from reactive.streams.base_objects.balancing_publisher import BalancingPublisher
import time


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestTroupeStageSupervisor:

    def test_creation(self, asys):
        actr = asys.createActor(TransientStageSupervisor)
        msg = TearDown(None, actr, None)
        asys.tell(actr, msg)
        asys.tell(actr, ActorExitRequest())

    def test_troupe_stage_supervisor(self, asys):
        actr = asys.createActor(TroupeStageSupervisor)
        msg = RegisterKlass(TroupeTestActor, actr, None)
        asys.tell(actr, msg)

        sub_pool = asys.createActor(RoundRobinSubscriptionPool)
        msg = SetSubscriptionPool(sub_pool, actr, None)
        asys.tell(actr, msg)

        src = asys.createActor(PublisherRandActor)
        msg = Subscribe(src, sub_pool, None)
        asys.tell(sub_pool, msg)

        pub = asys.createActor(BalancingPublisher)
        msg = SetPublisher(actr, pub, None)
        asys.tell(pub, msg)

        pll = Pull(100, pub, None)
        rval = asys.ask(pub, pll)
        assert isinstance(rval, Push)
        dt = time.time()
        while len(rval.payload) is 0 and time.time() - dt < 120:
            rval = asys.ask(pub, pll)
            assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) > 0
        for res in rval.payload:
            assert "Push" in res
        msg = TearDown(None, actr, None)
        asys.tell(actr, msg)
        asys.tell(actr, ActorExitRequest())
