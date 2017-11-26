'''
A logic source that handles pull requests through a logic publisher.  This
publisher requires the user to implement and provide a source actor.

This actor also acts as a supervisor for the actor created from the provided
actor class.

*Messages and Features*

This source routes messages to queues by logic so registering to the source
requires a special logic function.

- Pull = Pull up to n messages from the buffer
- Push = Push the batch to the result queue (beware of the drop policy)
- SetPublisher = Set the message publisher
- SetDropPolicy = Set the drop policy for the router (pop or ignore)
- SubscribeWithLogic = Subscribe to the publisher with a pickled logic function
- Desubscribe = Desubscribe from the publisherr
- GetPublisher = Return the publisher
- GetSubscribers = Get the subscribers


Created on Nov 17, 2017

@author: aevans
'''

from reactive.streams.base_objects.logic_publisher import LogicPublisher
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import RegisterKlass
from thespian.actors import ChildActorExited
from reactive.streams.objects.source import SourceBase


class LogicSource(LogicPublisher, SourceBase):

    def __init__(self):
        super(LogicSource, self).__init__()
        self.__pub_actor = None
        self.__klass = None

    def handle_klass_registration(self, msg, sender):
        """
        Handle registration of the klass.  The klass is a reference.  This
        actor creates the class.

        :param msg:  The message to handle with the class to supervise.
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__klass = msg.payload
        if self.__pub_actor:
            self.send(self.__pub_actor, ChildActorExited)
        self.__pub_actor = self.createActor(self.__klass)
        self.set_publisher_actor(self.__pub_actor)

    def handle_child_exit(self, msg, sender):
        """
        Handle a child actor exit.

        :param msg:  The message to handle with the actor payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.payload == self.__pub_actor:
            self.__pub_actor = self.createActor(self.__klass)

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, ChildActorExited):
                self.handle_child_exit(msg, sender)
            elif isinstance(msg, RegisterKlass):
                self.handle_klass_registration(msg, sender)
            else:
                LogicPublisher.receiveMessage(self, msg, sender)
                self.handle_message(msg, sender)
        except Exception:
            handle_actor_system_fail()
