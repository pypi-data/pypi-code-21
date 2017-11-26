'''
This module contains the TroupeStageActor.  This actor implements the methods
required by the Troupe Stage.  The user should overwrite the do_work method.

:WARNING: Do not overwrite the receiveMessage method.  To extend its functionality,
call this method through the superclass.

Created on Nov 13, 2017

@author: aevans
'''

from thespian.actors import ActorTypeDispatcher
from reactive.message.stream_messages import Push


class TroupeStageBase(ActorTypeDispatcher):
    """
    Stage base which does not implement the troupe decorator.  Extended classes
    need to implement the troupe decorator
    """

    def do_work(self, batch):
        """
        Overwrite.  This method handles the batch.  The entire batch is passed
        so that the programmer can properly handle each element. 
        """
        return batch

    def receiveMsg_Push(self, msg, sender):
        """
        Handle a message push, perform work, send on.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.troupe_work_in_progress = True
        if msg.sender:
            sender = msg.sender
        batch = msg.payload
        out_batch = self.do_work(batch)
        msg = Push(out_batch, sender, self.myAddress)
        self.send(sender, msg)
        self.troupe_work_in_progress = True
