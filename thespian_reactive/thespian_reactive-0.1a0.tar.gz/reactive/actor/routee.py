'''
An actor routee. There are special ways of asking the routee.
Any actor intended to be inside a router should be a routee

Created on Oct 29, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor
from reactive.error.handler import handle_actor_system_fail
from reactive.message.router_messages import RouteAsk, RouteTell, Broadcast


class ActorRoutee(BaseActor):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

    def on_receive(self, msg, sender):
        """
        Handle a received message.

        :param msg: Handle the incoming message
        :type msg: Message
        :param sender: Sender
        :type sender: Actor
        """
        pass

    def receiveMessage(self, msg, sender):
        """
        Receive a message.

        :param msg: The Message
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor()
        """
        try:
            if isinstance(msg, RouteAsk):
                sender = msg.sender
                msg = msg.payload
                if sender:
                    val = self.on_receive(msg, sender)
                    self.send(sender, val)
                elif msg.sender:
                    val = self.on_receive(msg, msg.sender)
                    self.send(msg.sender, val)
            elif isinstance(msg, RouteTell):
                self.on_receive(msg, msg.sender)
            elif isinstance(msg, Broadcast):
                payload = msg.payload
                sender = msg.sender
                self.on_receive(payload, sender)
        except Exception as e:
            handle_actor_system_fail()
