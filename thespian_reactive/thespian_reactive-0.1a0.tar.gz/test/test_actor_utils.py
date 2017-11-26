'''
Test common utilities

Created on Oct 29, 2017

@author: aevans
'''

import re
from thespian.actors import ActorSystem

from reactive.actor import name_creation_utils
from reactive.actor.base_actor import BaseActor
from reactive.actor.state import ActorState


class UtilTestActor(BaseActor):

    def receiveMessage(self, msg, sender):
        self.send(sender, self.state)


def test_name_generation():
    name = name_creation_utils.get_name()
    assert re.match("\d+\_\d+", name)


def test_base_actor_state():
    asys = ActorSystem("multiprocQueueBase")
    base = asys.createActor(UtilTestActor)
    state = asys.ask(base, "Get State")
    asys.shutdown()
    assert state is not None
    assert state == ActorState.CREATED
