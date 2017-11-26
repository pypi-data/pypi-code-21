'''
A balancing publisher acts as a buffer between a source actor and the graph.
A source actor must extended and provided.

Created on Nov 17, 2017

@author: aevans
'''


from reactive.streams.base_objects.balancing_publisher import BalancingPublisher
from reactive.error.handler import handle_actor_system_fail
from thespian.actors import ChildActorExited
from reactive.message.stream_messages import RegisterKlass


class BalancingSource(BalancingPublisher):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__klass = None
        self.__pub_actor = None

    def handle_klass_register(self, msg, sender):
        """
        Handle a class registration.

        :param msg:  The message with class class object payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__klass = msg.payload
        if self.__pub_actor:
            self.send(self.__pub_actor, ChildActorExited)
        self.__pub_actor = self.createACtor(self.__klass)

    def handle_child_actor_exited(self, msg, sender):
        """
        Handle a message when the child actor exits.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.payload == self.__pub_actor:
            self.__pub_actor = self.createActor(self.__pub_actor)

    def receiveMessage(self, msg, sender):
        """
        Handle a message on receipt

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            if isinstance(msg, RegisterKlass):
                self.handle_klass_register(msg, sender)
            elif isinstance(msg, ChildActorExited):
                self.handle_child_actor_exited(msg, sender)
            else:
                super().receiveMessage(msg, sender) 
        except Exception:
            handle_actor_system_fail()
