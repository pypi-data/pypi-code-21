'''
This source returns pulled data from an actor and stores it for processing
in a multi-queue publisher.  This class requires an actor extending source
actor to work.

Created on Nov 17, 2017

@author: aevans
'''

from reactive.streams.base_objects.multi_queue_publisher import MultiQPublisher
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import RegisterKlass
from thespian.actors import ChildActorExited
from reactive.streams.objects.source import SourceBase


class MultiQSource(MultiQPublisher, SourceBase):

    def __init__(self):
        """
        Constructor
        """
        super(MultiQSource, self).__init__()
        self.__klass = None
        self.__pub_actor = None

    def handle_klass_register(self, msg, sender):
        """
        Handle class registration.

        :param msg:  The message containing the actor payload
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
        Handle a child actor on exit.

        :param msg:  The actor message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.payload == self.__klass:
            self.createActor(self.__klass)

    def receiveMessage(self, msg, sender):
        """
        Handle a message on receipt

        :param msg:  The message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            if isinstance(msg, RegisterKlass):
                self.handle_klass_register(msg, sender)
            elif isinstance(msg, ChildActorExited):
                self.handle_child_exit(msg, sender)
            else:
                MultiQPublisher.receiveMessage(self, msg, sender)
                self.handle_message(msg, sender)
        except Exception:
            handle_actor_system_fail()
