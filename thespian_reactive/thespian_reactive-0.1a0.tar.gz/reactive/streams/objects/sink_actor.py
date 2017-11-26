'''
This actor implements the sink functions.  Users should override the on_push
function.

Created on Nov 17, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor
from reactive.message.stream_messages import Push, SetMaxBatchRequestSize, Pull
from reactive.error.handler import handle_actor_system_fail


class SinkActor(BaseActor):


    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__max_batch_size = 100

    def set_max_batch_size(self, msg, sender):
        """
        Sets the maximum batch size.

        :param msg:  The message with the int payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_size = msg.payload

    def do_push(self, batch, msg, sender):
        """
        Handle the push request.  The individual element, message, and sender
        are sent.

        :param batch:  The batch list
        :type batch:  list
        :param msg:  Message
        :type sender:  BaseActor
        """
        pass

    def __handle_push(self, msg, sender):
        """
        Handle a message push.

        :param msg:  The message with the list batch payload
        :type msg:  The Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        payload = msg.payload
        if isinstance(payload, list):
            self.on_push(payload, msg, sender)
        msg = Pull(self.__max_batch_size, sender, self)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        """
        Handle a message receipt.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            if isinstance(msg, Push):
                self.__handle_push(msg, sender)
            elif isinstance(msg, SetMaxBatchRequestSize):
                self.set_max_batch_size(msg, sender)
        except Exception:
            handle_actor_system_fail()
