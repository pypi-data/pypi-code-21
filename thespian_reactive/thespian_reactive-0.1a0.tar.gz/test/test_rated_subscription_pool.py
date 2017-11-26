'''
Test the rated subscription pool.

Created on Nov 7, 2017

@author: aevans
'''


import pytest
from thespian.actors import ActorSystem
from reactive.message.stream_messages import Pull, Push, Cancel
from test.modules.base_object_actors import PublisherStringActor, SubTest
from reactive.streams.base_objects.subscription import Subscription
from reactive.message.router_messages import Subscribe
from datetime import datetime
from reactive.streams.base_objects.rated_subscription_pool import RatedSubscriptionPool
from test.modules.object_work import get_work_batch_array
from datetime import timedelta
from reactive.message.stream_sub_pool_messages import SetSubscriber


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestRatedSubscriptionPool:

    def test_creation(self, asys):
        """
        Test the creation of a round robin subscription pool
        """
        rr = asys.createActor(RatedSubscriptionPool)
        cncl = Cancel(None, rr, None)
        asys.tell(rr, cncl)

    def test_push(self, asys):
        """
        Test a push from the subscription pool
        """
        rr = asys.createActor(RatedSubscriptionPool)
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
        rr = asys.createActor(RatedSubscriptionPool)

        suba = asys.createActor(Subscription)
        sub_puba = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_puba, suba, None)
        asys.tell(suba, ssn)
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)

        subb = asys.createActor(Subscription)
        sub_pubb = asys.createActor(PublisherStringActor)
        ssn = SetSubscriber(sub_pubb, subb, None)
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
        i = 0
        while i < 100 and tstart - datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
            if len(rval.payload) > 0:
                i += 1
        assert i == 100
        assert len(rval.payload) is 50
