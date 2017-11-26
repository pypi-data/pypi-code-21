'''
Test the logic based publisher.

Created on Nov 8, 2017

@author: aevans
'''

import dill
import base64
from datetime import datetime, timedelta
import pytest
from thespian.actors import ActorSystem
from reactive.streams.base_objects.multi_queue_publisher import MultiQPublisher
from test.modules.base_object_actors import PublisherStringActor, SubTest,\
    PublisherRandActor
from reactive.message.stream_messages import SetPublisher, Pull,\
    Push, GetPublisher
from reactive.streams.base_objects.rated_subscription_pool import RatedSubscriptionPool
from reactive.streams.base_objects.subscription import Subscription
from reactive.message.router_messages import Subscribe, DeSubscribe
from reactive.streams.base_objects.logic_publisher import LogicPublisher
from reactive.message.stream_sub_pool_messages import GetSubscribers,\
    SubscribeWithLogic, SetSubscriber


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestLogicPublisher():

    def lt_100(self, payload):
        """
        Test if the payload is less then 100
        """
        if payload < 100:
            return True
        return False

    def gte_100(self, payload):
        """
        Test if the load is greater than 100
        """
        if payload >= 100:
            return True
        return False

    def test_creation(self, asys):
        """
        Test a publisher creation
        """
        pub = asys.createActor(MultiQPublisher)


    def test_set_publisher(self, asys):
        """
        Test setting the publisher
        """
        pub = asys.createActor(LogicPublisher)
        spa = asys.createActor(PublisherStringActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)
        get_pub = GetPublisher(None, msg, None)
        rval = asys.ask(pub, get_pub)
        assert isinstance(rval, GetPublisher)
        assert rval.payload is not None

    def test_subscribe(self, asys):
        """
        Test subscribing
        """
        pub = asys.createActor(LogicPublisher)
        spa = asys.createActor(PublisherStringActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)
        get_pub = GetPublisher(None, msg, None)

        rr = asys.createActor(RatedSubscriptionPool)

        suba = asys.createActor(Subscription)
        get_func = dill.dumps(self.gte_100)
        get_funcb = base64.b64encode(get_func)
        rrs = SubscribeWithLogic(suba, get_funcb, rr, None)
        asys.tell(pub, rrs)
        msg = GetSubscribers(None, pub, None)
        rval = asys.ask(pub, msg)
        assert isinstance(rval, GetSubscribers)
        assert isinstance(rval.payload, dict)
        load = rval.payload
        assert len(load.keys()) == 1

    def test_desubscribe(self, asys):
        """
        Test desubscription
        """
        pub = asys.createActor(LogicPublisher)
        spa = asys.createActor(PublisherStringActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)
        get_pub = GetPublisher(None, msg, None)

        rr = asys.createActor(RatedSubscriptionPool)

        suba = asys.createActor(Subscription)
        get_func = dill.dumps(self.gte_100)
        get_funcb = base64.b64encode(get_func)
        rrs = SubscribeWithLogic(suba, get_funcb, rr, None)
        asys.tell(pub, rrs)
        ds = DeSubscribe(suba, pub, None)
        asys.tell(pub, ds)
        msg = GetSubscribers(None, pub, None)
        rval = asys.ask(pub, msg)
        assert isinstance(rval, GetSubscribers)
        assert isinstance(rval.payload, dict)
        load = rval.payload
        assert len(load.keys()) == 0

    def test_push_pull_with_pub(self, asys):
        """
        Test the push and pull
        """
        # create pub
        pub = asys.createActor(LogicPublisher)
        spa = asys.createActor(PublisherRandActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)

        #setup the functions to use
        get_func = dill.dumps(self.gte_100)
        get_funcb = base64.b64encode(get_func)

        # create pool
        rr = asys.createActor(RatedSubscriptionPool)

        #create a subscription with a specific publisher
        suba = asys.createActor(Subscription)
        msg = SetSubscriber(pub, suba, None)
        asys.tell(suba, msg)

        # add the subscriber to the pool
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)

        # tell the publisher about the subscriber and logic
        # to use with subscriber
        pubsl = SubscribeWithLogic(suba, get_funcb,  pub, None)
        asys.tell(pub, pubsl)

        # set the pools publisher
        msg = SetPublisher(pub, rr, None)
        asys.tell(rr, msg)
        
        #create the fake stage and set its subscription pool
        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)

        #begin pull test
        pll = Pull(50, rr, None)
        rval = asys.ask(st, pll)
        assert isinstance(rval, Push)
        assert isinstance(rval.payload, list)
        assert len(rval.payload) is 0
        tstart = datetime.now()
        i = 0
        while i < 10 and tstart - datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
            if len(rval.payload) > 0:
                i += 1
        assert i == 10
        assert len(rval.payload) > 0
        assert len(rval.payload) <= 50
        

    def test_push_pull_with_multi_pub(self, asys):
        """
        Test the push and pull
        """
        # create pub
        pub = asys.createActor(LogicPublisher)
        spa = asys.createActor(PublisherRandActor)
        msg = SetPublisher(spa, pub, None)
        asys.tell(pub, msg)
        get_func = dill.dumps(self.gte_100)
        get_funcb = base64.b64encode(get_func)
        get_func = dill.dumps(self.lt_100)
        get_funcbb = base64.b64encode(get_func) 

        # create pool
        rr = asys.createActor(RatedSubscriptionPool)

        #create a subscription with a specific publisher
        suba = asys.createActor(Subscription)
        msg = SetSubscriber(pub, suba, None)
        asys.tell(suba, msg)

        subb = asys.createActor(Subscription)
        msg = SetSubscriber(pub, subb, None)
        asys.tell(subb, msg)

        # add the subscriber to the pool
        rrs = Subscribe(suba, rr, None)
        asys.tell(rr, rrs)
        
        rrs = Subscribe(subb, rr, None)
        asys.tell(rr, rrs)

        # tell the publisher about the subscriber and logic
        # to use with subscriber
        pubsl = SubscribeWithLogic(suba, get_funcb, pub, None)
        asys.tell(pub, pubsl)

        pubsl = SubscribeWithLogic(subb, get_funcbb, pub, None)
        asys.tell(pub, pubsl)

        # set the pools publisher
        msg = SetPublisher(pub, rr, None)
        asys.tell(rr, msg)
        
        #create the fake stage and set its subscription pool
        st = asys.createActor(SubTest)
        msg = Subscribe(rr, st, None)
        asys.tell(st, msg)

        #begin pull test
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

            if len(rval.payload) is 0:
                rval = asys.ask(st, pll)

            if len(rval.payload) > 0:
                i += 1
        assert i == 100
        assert len(rval.payload) > 0
        assert len(rval.payload) <= 50
