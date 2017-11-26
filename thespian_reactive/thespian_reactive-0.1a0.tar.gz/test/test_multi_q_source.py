'''
Test the balancing source.

Created on Nov 17, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem
from test.modules.streams.stream_source import StringSource
from reactive.message.stream_messages import SetPublisher, Pull, Push,\
    RegisterKlass
from reactive.streams.objects.multi_queue_source import MultiQSource
from reactive.streams.base_objects.rated_subscription_pool import RatedSubscriptionPool
from reactive.streams.base_objects.subscription import Subscription
from reactive.message.stream_sub_pool_messages import SetSubscriber
from reactive.message.router_messages import Subscribe
from test.modules.base_object_actors import SubTest, PublisherStringActor
import datetime
from _datetime import timedelta


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()

class TestMultiQSource():

    def test_creation(self, asys):
        sactor = asys.createActor(StringSource)
        actor = asys.createActor(MultiQSource)
        msg = SetPublisher(sactor, None, None)
        asys.tell(actor, msg)

    def test_push_pull_with_pub(self, asys):
        """
        Test the push and pull
        """
        pub = asys.createActor(MultiQSource)
        spa = PublisherStringActor
        msg = RegisterKlass(spa, pub, None)
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
        tstart = datetime.datetime.now()
        i = 0
        while i < 100 and tstart - datetime.datetime.now() <  timedelta(seconds=120):
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
        pub = asys.createActor(MultiQSource)
        spa = PublisherStringActor
        msg = RegisterKlass(spa, pub, None)
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
        tstart = datetime.datetime.now()
        i = 0
        while i < 100 and tstart - datetime.datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
            if len(rval.payload) > 0:
                i += 1
        assert i == 100
        assert len(rval.payload) is 50
