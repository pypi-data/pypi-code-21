'''
Test a Publisher.

Created on Nov 2, 2017

@author: aevans
'''


import pytest
from thespian.actors import ActorSystem

from reactive.streams.base_objects.publisher import Publisher
from test.modules.base_object_actors import PublisherStringActor
from reactive.message.router_messages import Subscribe, DeSubscribe
from reactive.message.stream_messages import SetPublisher, GetPublisher
from reactive.message.stream_sub_pool_messages import GetSubscribers


@pytest.fixture(scope="module")
def asys():
    return ActorSystem()


class TestPublisher():

    def test_creation(self, asys):
        """
        Basic creation test
        """
        pub = asys.createActor(Publisher)

    def test_subscription(self, asys):
        """
        Test a subscription to a publisher
        """
        pub = asys.createActor(Publisher)
        ps = asys.createActor(PublisherStringActor)
        gs = GetSubscribers(None, pub, None)
        msg = Subscribe(ps, pub, None)
        asys.tell(pub, msg)
        rval = asys.ask(pub, gs)
        assert isinstance(rval, GetSubscribers)
        assert len(rval.payload) == 1

    def test_desubscription(self, asys):
        """
        Test subscription and desubscription
        """
        pub = asys.createActor(Publisher)
        gs = GetSubscribers(None, pub, None)
        ps = asys.createActor(PublisherStringActor)
        msg = Subscribe(ps, pub, None)
        asys.tell(pub, msg)
        rval = asys.ask(pub, gs)
        assert isinstance(rval, GetSubscribers)
        assert len(rval.payload) == 1
        ds = DeSubscribe(ps, pub, None)
        asys.tell(pub, ds)
        rval = asys.ask(pub, gs)
        assert isinstance(rval, GetSubscribers)
        assert len(rval.payload) == 0

    def test_set_publisher(self, asys):
        """
        Test setting the publisher
        """
        pub = asys.createActor(Publisher)
        gp = GetPublisher(None, pub, None)
        ps = asys.createActor(PublisherStringActor)
        msg = SetPublisher(ps, pub, None)
        asys.tell(pub, msg)
        rval = asys.ask(pub, gp)
        assert isinstance(rval, GetPublisher)
