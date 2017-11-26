'''
Created on Nov 2, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor
from reactive.message.stream_messages import Push, Pull
from reactive.error.handler import handle_actor_system_fail


class StringBatchTestActor(BaseActor):
    """
    Test actor for subscription
    """
    def __init__(self):
        super().__init__()
        self.__index = 0

    def handle_pull(self, msg, sender):
        batch_size = msg.payload
        batch = []
        for i in range(0, batch_size):
            batch.append("Receipt {}".format(self.__index))
        msg  = Push(batch, sender, self)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, Pull):
                self.handle_pull(msg, sender)
        except Exception:
            handle_actor_system_fail()
