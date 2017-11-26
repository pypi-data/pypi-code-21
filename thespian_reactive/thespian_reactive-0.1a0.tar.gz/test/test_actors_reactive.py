'''
Some basics for learning.

Created on Oct 29, 2017

@author: aevans
'''

import logging
import pytest
from thespian.actors import Actor, ActorSystem

from reactive.message.base_message import Message


class SourceMessage(Message):
    pass

class SourceAsk(Message):
    pass

class TargetMessage(Message):
    pass


class DoTestSource(Actor):

    def receiveMessage(self, msg, sender):
        print(msg)
        if isinstance(msg, TargetMessage):
            msg = "Received Message From {} via {}".format(msg, sender)
            logging.info(msg)
        elif isinstance(msg, SourceMessage):
            if msg.sender is None:
                msg.sender = self
            self.send(msg.target, msg)


class DoTestTarget(Actor):

    def receiveMessage(self, message, sender):
        if isinstance(message, SourceMessage):
            self.send(sender, 'Received a Message {}'.format(message.payload))
        elif isinstance(message, SourceAsk):
            self.send(sender, "Received {}".format(str(message)))
        else:
            logging.info("Received {}".format(str(message)))


class TestActorSystem():

    def test_tell(self):
        asys = ActorSystem('multiprocTCPBase')
        source = asys.createActor(DoTestSource)
        targ = asys.createActor(DoTestTarget)
        msg = SourceMessage("Hello From Source", target=targ, sender=source)
        logging.info("Sending {}".format(str(msg)))
        asys.tell(targ, msg)

    def test_ask(self):
        print("Testing ask")
        asys = ActorSystem('multiprocTCPBase')
        source = asys.createActor(DoTestSource)
        targ = asys.createActor(DoTestTarget)
        msg = SourceAsk("Hello From Source", target=targ, sender=source)
        logging.info("Sending {}".format(str(msg)))
        print(asys.ask(targ, msg))
        asys.shutdown()

if __name__ == "__main__":
    tc = TestActorSystem()
    tc.test_ask()
