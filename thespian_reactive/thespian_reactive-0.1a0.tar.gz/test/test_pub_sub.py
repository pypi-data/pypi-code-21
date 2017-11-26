'''
Created on Oct 29, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem

from reactive.actor.routee import ActorRoutee
from reactive.message.base_message import Message
from reactive.message.router_messages import Subscribe, GetNumRoutees, \
    DeSubscribe, Broadcast, RouteAsk
from reactive.routers.pub_sub import PubSub


class RouteeAdd(Message):
    pass


class RouteeAddResponse(Message):
    pass


class PubTestRoutee(ActorRoutee):

    def __init__(self):
        super().__init__()

    def on_receive(self, msg, sender):
        super().receiveMessage(msg, sender)
        if isinstance(msg, RouteeAdd):
            payload = msg.payload
            payload += 1
            add_resp = RouteeAddResponse(payload, sender, self)
            return add_resp


@pytest.fixture(scope="module")
def asys():
    #asys = ActorSystem("multiprocQueueBase")
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestPubSub():

    def test_creation(self, asys):
        asys.createActor(PubSub)

    def test_subscribe_routee(self, asys):
        psub = asys.createActor(PubSub)
        routee = asys.createActor(PubTestRoutee)
        sub = Subscribe(routee, psub, None)
        asys.tell(psub, sub)
        count_msg = GetNumRoutees(None, psub, None)
        ct = asys.ask(psub, count_msg)
        assert ct == 1

    def test_desubscribe(self, asys):
        psub = asys.createActor(PubSub)
        routee = asys.createActor(PubTestRoutee)
        routeeb = asys.createActor(PubTestRoutee)
        sub = Subscribe(routee, psub, None)
        asys.tell(psub, sub)
        subb = Subscribe(routeeb, psub, None)
        asys.tell(psub, subb)
        count_msg = GetNumRoutees(None, psub, None)
        desub = DeSubscribe(routee, psub, None)
        asys.tell(psub, desub)
        ct = asys.ask(psub, count_msg)
        assert ct == 1

    def test_broadcast(self, asys):
        psub = asys.createActor(PubSub)
        routee = asys.createActor(PubTestRoutee)
        routeeb = asys.createActor(PubTestRoutee)
        sub = Subscribe(routee, psub, None)
        asys.tell(psub, sub)
        subb = Subscribe(routeeb, psub, None)
        asys.tell(psub, subb)
        bmsg = Broadcast("Hello", psub, None)
        asys.tell(psub, bmsg)

    def test_ask_routee(self, asys):
        psub = asys.createActor(PubSub)
        routee = asys.createActor(PubTestRoutee)
        routeeb = asys.createActor(PubTestRoutee)
        sub = Subscribe(routee, psub, None)
        asys.tell(psub, sub)
        subb = Subscribe(routeeb, psub, None)
        asys.tell(psub, subb)
        radd = RouteeAdd(1, psub, None)
        rask = RouteAsk(radd, psub, None)
        res_val = asys.ask(psub, rask)
        assert res_val.payload == 2
