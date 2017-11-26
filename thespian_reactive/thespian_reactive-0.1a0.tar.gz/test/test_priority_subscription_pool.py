'''
Test a priority subscription pool

Created on Nov 6, 2017

@author: aevans
'''

import pytest
from reactive.streams.base_objects.priority_subscription_pool import PrioritySubscriptionPool,\
    PriorityQueueType
from reactive.message.stream_messages import Cancel, Push, Pull
from reactive.message.router_messages import Subscribe
from test.modules.base_object_actors import SubTest, PublisherStringActor
from test.modules.object_work import get_work_batch_array
from reactive.streams.base_objects.subscription import Subscription
from datetime import datetime
from _datetime import timedelta
from thespian.actors import ActorSystem
from time import sleep
from reactive.message.stream_sub_pool_messages import SetSubscriber,\
    SubscribeWithPriority
from reactive.message.stream_priority_messages import GetPriorityQueueType,\
    SetPriorityQueueType


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestPrioritySubscriptionPool:

    def stest_creation(self, asys):
        """
        Test the creation of a round robin subscription pool
        """
        rr = asys.createActor(PrioritySubscriptionPool)
        cncl = Cancel(None, rr, None)
        asys.tell(rr, cncl)

    def stest_push(self, asys):
        """
        Test a push from the subscription pool
        """
        rr = asys.createActor(PrioritySubscriptionPool)
        sub = asys.createActor(SubTest) 
        msg = Subscribe(sub, rr, None)
        asys.tell(rr, msg)
        work = get_work_batch_array
        msg = Push(work, rr, None)
        asys.tell(rr, msg)
        cncl = Cancel(None, rr, None)
        asys.tell(rr, cncl)

    def stest_set_queue_type(self, asys):
        """
        Test setting the queue type.
        """
        sp = asys.createActor(PrioritySubscriptionPool)
        msg = GetPriorityQueueType(None, None, None)
        rval = asys.ask(sp, msg, timeout=120)
        assert isinstance(rval, GetPriorityQueueType)
        assert rval.payload == PriorityQueueType.EMPTY_RATED
        msg = SetPriorityQueueType(PriorityQueueType.MULTIQUEUE, None, None)
        asys.tell(sp, msg)
        msg = GetPriorityQueueType(None, None, None)
        rval = asys.ask(sp, msg, timeout=120)
        assert isinstance(rval, GetPriorityQueueType)
        assert rval.payload == PriorityQueueType.MULTIQUEUE

    def test_pull_empty_rated(self, asys):
        """
        Test a pull from the subscription pool
        """
        rr = asys.createActor(PrioritySubscriptionPool)

        suba = asys.createActor(Subscription)
        sub_puba = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_puba, suba, None)
        asys.tell(suba, ssn)
        rrs = SubscribeWithPriority(suba, 2, rr, None)
        asys.tell(rr, rrs)

        subb = asys.createActor(Subscription)
        sub_pubb = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_pubb, subb, None)
        asys.tell(subb, ssn)
        rrs = SubscribeWithPriority(subb, 1, rr, None)
        asys.tell(rr, rrs)
        
        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)

        pll = Pull(50, rr, None)
        rval = asys.ask(st, pll)
        assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) is 0
        tstart = datetime.now()
        while len(rval.payload) is 0 and tstart - datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
        assert len(rval.payload) is 50

    def test_pull_priority_queue(self, asys):
        """
        Test a pull from the subscription pool
        """
        rr = asys.createActor(PrioritySubscriptionPool)
        msg = SetPriorityQueueType(PriorityQueueType.MULTIQUEUE, None, None)
        asys.tell(rr, msg)

        suba = asys.createActor(Subscription)
        sub_puba = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_puba, suba, None)
        asys.tell(suba, ssn)
        rrs = SubscribeWithPriority(suba, 2, rr, None)
        asys.tell(rr, rrs)

        subb = asys.createActor(Subscription)
        sub_pubb = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_pubb, subb, None)
        asys.tell(subb, ssn)
        rrs = SubscribeWithPriority(subb, 1, rr, None)
        asys.tell(rr, rrs)
        
        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)

        pll = Pull(50, rr, None)
        rval = asys.ask(st, pll)
        assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) is 0
        tstart = datetime.now()
        while len(rval.payload) is 0 and tstart - datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
        assert len(rval.payload) is 50
