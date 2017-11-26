"""
Fake subscription pool that sends back a payload size int list.

@author: aevans
"""

from thespian.actors import ActorTypeDispatcher
from reactive.message.stream_messages import Push
import pdb


class FakeSub(ActorTypeDispatcher):

    def __init__(self):
        super().__init__()

    def receiveMsg_Pull(self, msg, sender):
        if msg.sender:
            sender = msg.sender
        batch = []
        batch_size = msg.payload
        for i in range(0, batch_size):
            batch.append(i)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
