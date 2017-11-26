'''
Round Robin Subscription Pool test

Created on Nov 5, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem
from reactive.streams.base_objects.round_robin_subscription_pool import RoundRobinSubscriptionPool
from reactive.message.stream_messages import Cancel, Push, Pull
from reactive.message.router_messages import Subscribe
from reactive.streams.base_objects.subscription import Subscription
from test.modules.object_work import get_work_batch_array
from test.modules.base_object_actors import PublisherStringActor, SubTest
from datetime import timedelta, datetime
from reactive.message.stream_sub_pool_messages import SetSubscriber


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()
        

class TestRoundRobinSubscriptionPool:

    def test_creation(self, asys):
        """
        Test the creation of a round robin subscription pool
        """
        rr = asys.createActor(RoundRobinSubscriptionPool)
        cncl = Cancel(None, rr, None)
        asys.tell(rr, cncl)

    def test_push(self, asys):
        """
        Test a push from the subscription pool
        """
        rr = asys.createActor(RoundRobinSubscriptionPool)
        sub = asys.createActor(SubTest) 
        msg = Subscribe(sub, rr, None)
        asys.tell(rr, msg)
        work = get_work_batch_array()
        msg = Push(work, rr, None)
        asys.tell(rr, msg)
        cncl = Cancel(None, rr, None)
        asys.tell(rr, cncl)

    def test_pull(self, asys):
        """
        Test a pull from the subscription pool
        """
        rr = asys.createActor(RoundRobinSubscriptionPool)

        suba = asys.createActor(Subscription)
        sub_puba = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_puba, suba, None)
        asys.tell(suba, ssn)
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)

        subb = asys.createActor(Subscription)
        sub_pubb = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_pubb, suba, None)
        asys.tell(subb, ssn)
        rrs = Subscribe(subb, rr, None)
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
