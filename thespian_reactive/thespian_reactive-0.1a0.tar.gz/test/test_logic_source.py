'''
Test the balancing source.

Created on Nov 17, 2017

@author: aevans
'''

import base64
import pytest
from thespian.actors import ActorSystem
from test.modules.streams.stream_source import StringSource
from reactive.message.stream_messages import SetPublisher, Pull, Push,\
    RegisterKlass, SetRabbitExchange, GetStatisticsViaRabbitMQ, TearDown
from reactive.streams.base_objects.rated_subscription_pool import RatedSubscriptionPool
from reactive.streams.base_objects.subscription import Subscription
from reactive.message.stream_sub_pool_messages import SetSubscriber,\
    SubscribeWithLogic
from reactive.message.router_messages import Subscribe
from test.modules.base_object_actors import SubTest, PublisherRandActor
import datetime
from _datetime import timedelta
from reactive.streams.objects.logic_source import LogicSource
import dill
from multiprocessing import Process
import json
from test.modules.streams.source import StringTestSource
import pika


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()

class TestLogicSource():

    def test_creation(self, asys):
        sactor = asys.createActor(StringSource)
        actor = asys.createActor(LogicSource)
        msg = SetPublisher(sactor, None, None)
        asys.tell(actor, msg)

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

    def test_pull(self, asys):
        # create pub
        pub = asys.createActor(LogicSource)
        spa = PublisherRandActor
        msg = RegisterKlass(spa, pub, None)
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
        tstart = datetime.datetime.now()
        i = 0
        while i < 10 and tstart - datetime.datetime.now() <  timedelta(seconds=120):
            pll = Pull(50, st, None)
            rval = asys.ask(st, pll)
            if len(rval.payload) > 0:
                i += 1
        assert i == 10
        assert len(rval.payload) > 0
        assert len(rval.payload) <= 50

    def stest_get_stats(self, asys, msg_queue):
        def close_callback(ch, method, properties, body):
            print("Closing")
    
        def cancel_callbck(ch, method, properties, body):
            print("Cancelled")
    
        def callback(ch, method, properties, body):
            print(body)
            msg_queue.put_nowait(body)
        src = asys.createActor(StringTestSource)
        pars = pika.ConnectionParameters('localhost', port = 5672)
        connection = pika.BlockingConnection(pars)
        channel = connection.channel()
        channel.queue_declare(queue='source_test')
        channel.basic_consume(callback,
                              queue="source_test",
                              no_ack=True,
                              consumer_tag="cbck")
        proc = Process(target=channel.start_consuming)
        proc.start()
        msg = SetRabbitExchange('', "source_test", "localhost", None, src, None)
        asys.tell(src, msg)
        msg = GetStatisticsViaRabbitMQ(None, src, None)
        asys.tell(src, msg)
        rval = None
        try:
            rval = msg_queue.get(timeout=120)
            assert rval is not None
            assert isinstance(rval, bytes)
            rj = json.loads(rval.decode("utf-8"))
            assert rj['errors'] == 0
        finally:
            msg = TearDown(None, src, None)
            asys.tell(src, msg)
            print("Closing Thread")
            proc.terminate()

