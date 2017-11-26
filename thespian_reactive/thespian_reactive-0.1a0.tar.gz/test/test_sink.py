'''
Created on Nov 9, 2017

@author: aevans
'''

import pika
import pytest
from thespian.actors import ActorSystem
from reactive.streams.objects.sink import BaseSink
from test.modules.base_object_actors import PublisherRandActor
from reactive.message.stream_work_stage_messages import SetSubscriptionPool
from atomos.atomic import AtomicInteger
from reactive.message.stream_messages import Start, TearDown


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class STestSink:

    def test_creation(self, asys):
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        num = AtomicInteger(0)
        def callback(ch, method, properties, body):
            print(" [x] Received %r".format(body))
            num.get_and_add(1)
            if num.get() is 10:
                connection.close()
        channel = connection.channel()
        channel.queue_declare(queue='test_sink')
        channel.basic_consume(callback,
                      queue='test_sink',
                      no_ack=True)
        sink = asys.createActor(BaseSink)
        pub = asys.createActor(PublisherRandActor)
        msg = SetSubscriptionPool(pub, sink, None)
        asys.tell(sink, msg)
        #msg = RegisterKlass(SinkTestProcess, sink, None)
        asys.tell(sink, msg)
        
        msg = Start(None, pub, None)
        asys.tell(sink, msg)
        while num.get() < 10:
            pass
        msg= TearDown(None, sink, None)
        asys.tell(sink, msg)
