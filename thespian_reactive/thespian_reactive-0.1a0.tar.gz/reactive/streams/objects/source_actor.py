'''
This is the source actor.  Users should implement and provide the on_pull
function.

Created on Nov 17, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor
from reactive.message.stream_messages import Push, Pull
from reactive.error.handler import handle_actor_system_fail


class SourceActor(BaseActor):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

    def do_pull(self, msg, sender):
        """
        User overwritten method dictating how the pull works.

        :return:  The processed batch
        :rtype:  list
        """
        return []

    def next(self, msg, sender):
        """
        Get the next batch using the user method.

        :param msg:  The message with the int payload of the next batch size
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        payload = msg.payload
        batch = []
        if isinstance(payload, int):
            for i in range(0, payload):
                rval = self.do_pull(msg, sender)
                batch.append(rval)
        msg = Push(batch, sender, self)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, Pull):
                self.next(msg, sender)
            else:
                super().receiveMessage(msg, sender)
        except Exception:
            handle_actor_system_fail()
