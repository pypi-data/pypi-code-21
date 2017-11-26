'''
Test the source actor.

Created on Nov 9, 2017

@author: aevans
'''

from multiprocessing import Queue, Process
import pika
import pytest
from thespian.actors import ActorSystem
from test.modules.streams.source import StringTestSource
from reactive.message.stream_messages import Pull, Push,\
    GetStatisticsViaRabbitMQ, SetRabbitExchange, TearDown
import json


@pytest.fixture(scope="module")
def asys():
    #asys = ActorSystem("multiprocQueueBase")
    asys = ActorSystem()
    yield asys
    asys.shutdown()


@pytest.fixture(scope="module")
def msg_queue():
    q = Queue(maxsize=1000)
    return q

class TestBasicSource:
    
    def test_creation(self, asys):
        src = asys.createActor(StringTestSource)

    def test_pull(self, asys):
        # setup basic source
        src = asys.createActor(StringTestSource)
        
        # test demand from source
        msg = Pull(100, None, None)
        for i in range(0, 10):
            rval = asys.ask(src, msg)
            assert isinstance(rval, Push)
            assert isinstance(rval.payload, list)
            assert len(rval.payload) == 100
            for res in rval.payload:
                assert isinstance(res, str)
                assert "Pull" in res

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
