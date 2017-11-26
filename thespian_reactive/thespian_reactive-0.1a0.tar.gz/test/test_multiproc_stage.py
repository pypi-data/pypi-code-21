'''
Test the multiprocessing stage.

Created on Nov 11, 2017

@author: aevans
'''

import pika
import pytest
from thespian.actors import ActorSystem


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


@pytest.fixture(scope="module")
def rq():
    conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = conn.channel()
    channel.queue_declare("general_streams")
    yield channel
    channel.queue_delete("general_streams")
    channel.close()


class TestMultiProcessingStage:

    def test_creation(self):
        pass

    def test_stage_setup(self):
        pass

    def test_stream_component(self):
        """
        Test a basic stream with stage and queue sink.
        """
        pass
