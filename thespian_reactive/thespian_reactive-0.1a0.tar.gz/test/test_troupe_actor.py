'''
Test the troupe actor with the troupe decorator.

Created on Nov 20, 2017

@author: aevans
'''

import pytest
from thespian.actors import ActorSystem, ActorExitRequest
from test.modules.troupes.basic import TroupeTestActor
from reactive.message.stream_messages import Push


@pytest.fixture(scope="module")
def asys():
    asys = ActorSystem()
    yield asys
    asys.shutdown()


class TestTroupe:

    def test_creation(self, asys):
        actr = asys.createActor(TroupeTestActor)
        asys.tell(actr, ActorExitRequest())

    def test_work_batch(self, asys):
        actr = asys.createActor(TroupeTestActor)
        batch = [1,2,3,4,5]
        msg = Push(batch, actr, None)
        rval = asys.ask(actr, msg)
        assert isinstance(rval, Push)
        load = rval.payload
        assert isinstance(load, list)
        assert len(load) is 5
        for rstr in load:
            assert "Push" in rstr
        asys.tell(actr, ActorExitRequest())
