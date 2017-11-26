'''
Test the transient stage supervisor.

Created on Nov 24, 2017Te

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem, ActorExitRequest
from reactive.streams.objects.transient_stage_supervisor import TransientStageSupervisor
from reactive.message.stream_messages import TearDown, SetPublisher, Pull, Push
from reactive.message.stream_work_stage_messages import TransientStageSettings,\
    SetSubscriptionPool
from test.modules.transient.basic import TransientTestActor
from reactive.streams.base_objects.round_robin_subscription_pool import RoundRobinSubscriptionPool
from reactive.streams.base_objects.balancing_publisher import BalancingPublisher
from test.modules.base_object_actors import PublisherRandActor
from reactive.message.router_messages import Subscribe
import time
from reactive.routers.router_type import RouterType


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestTransientStageSupervisor:

    def test_creation(self, asys):
        actr = asys.createActor(TransientStageSupervisor)
        msg = TearDown(None, actr, None)
        asys.tell(actr, msg)
        asys.tell(actr, ActorExitRequest())

    def test_transient_stage_supervisor(self, asys):
        actr = asys.createActor(TransientStageSupervisor)
        sub_pool = asys.createActor(RoundRobinSubscriptionPool)
        msg = SetSubscriptionPool(sub_pool, actr, None)
        asys.tell(actr, msg)
        src = asys.createActor(PublisherRandActor)
        msg = Subscribe(src, sub_pool, None)
        asys.tell(sub_pool, msg)
        msg = TransientStageSettings(payload=TransientTestActor, min_count=1,
                                     max_count=3, router_type=RouterType.ROUND_ROBIN,
                                     target=actr, sender=None)
        asys.tell(actr, msg)

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
            assert "Pull" in res
        msg = TearDown(None, actr, None)
        asys.tell(actr, msg)
        asys.tell(actr, ActorExitRequest())
