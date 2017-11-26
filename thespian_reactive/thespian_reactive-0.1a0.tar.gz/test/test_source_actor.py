'''
Test a source actor

Created on Nov 17, 2017

@author: aevans
'''


import pytest
from thespian.actors import ActorSystem, ActorExitRequest
from test.modules.streams.stream_source import StringSource
from reactive.message.stream_messages import Pull, Push


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestSourceActor():

    def test_creation(self, asys):
        src = asys.createActor(StringSource)
        msg = ActorExitRequest()
        asys.tell(src, msg)

    def test_pull(self, asys):
        src = asys.createActor(StringSource)
        for i in range(0, 10):
            msg = Pull(100, None, None)
            rval = asys.ask(src, msg)
            assert isinstance(rval, Push)
            assert isinstance(rval.payload, list)
            assert len(rval.payload) > 0
            for result in rval.payload:
                assert isinstance(result, str)
                assert "Pull" in result
