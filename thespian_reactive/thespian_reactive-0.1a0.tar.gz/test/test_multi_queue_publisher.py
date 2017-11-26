'''
Test a publisher with a queue per subscriber.

Created on Nov 8, 2017

@author: aevans
'''

from datetime import datetime
import pytest
from thespian.actors import ActorSystem
from reactive.streams.base_objects.multi_queue_publisher import MultiQPublisher
from reactive.message.stream_messages import Push, Pull, SetPublisher
from test.modules.base_object_actors import PublisherStringActor, SubTest
from reactive.streams.base_objects.rated_subscription_pool import RatedSubscriptionPool
from reactive.streams.base_objects.subscription import Subscription
from reactive.message.router_messages import Subscribe
from _datetime import timedelta
from reactive.message.stream_sub_pool_messages import SetSubscriber


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestMultiQueuePublisher:

    def test_creation(self, asys):
        """
        Test a publisher creation
        """
        pub = asys.createActor(MultiQPublisher)

    def test_push_pull_with_pub(self, asys):
        """
        Test the push and pull
        """
        pub = asys.createActor(MultiQPublisher)
        spa = asys.createActor(PublisherStringActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)

        rr = asys.createActor(RatedSubscriptionPool)

        suba = asys.createActor(Subscription)
        ssn = SetSubscriber(pub, suba, None)
        asys.tell(suba, ssn)
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)
        asys.tell(pub, rrs)

        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)
        asys.tell(pub, rrs)

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

    def test_push_pull_with_multi_pub(self, asys):
        """
        Test the push and pull
        """
        pub = asys.createActor(MultiQPublisher)
        spa = asys.createActor(PublisherStringActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)

        rr = asys.createActor(RatedSubscriptionPool)

        suba = asys.createActor(Subscription)
        ssn = SetSubscriber(pub, suba, None)
        asys.tell(suba, ssn)
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)
        asys.tell(pub, rrs)

        subb = asys.createActor(Subscription)
        ssn = SetSubscriber(pub, subb, None)
        asys.tell(subb, ssn)
        rrs = Subscribe(subb, rr, None)
        asys.tell(rr, rrs)
        asys.tell(pub, rrs)

        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)
        asys.tell(pub, rrs)

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
