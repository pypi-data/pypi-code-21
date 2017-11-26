'''
A basic supervisor for monitoring objects.

Created on Nov 20, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import RegisterKlass
from thespian.actors import ChildActorExited


class Supervisor(BaseActor):

    def __init__(self):
        super().__init__()
        self.__klass = None

    def handle_restart(self):
        """
        Overwrite.  Restart the actor.  Called when a child exits.
        """
        pass

    def handle_actor_exit(self, msg, sender):
        """
        Handle a message on actor exit by.  Calls handle_restart when a child
        actor exits.

        :param msg:  The message to handle.
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if self.__klass:
            self.handle_restart()

    def handle_register_klass(self, msg, sender):
        """
        Handle class registration.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__klass = msg.payload

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, RegisterKlass):
                self.handle_register_klass(msg, sender)
            elif isinstance(msg, ChildActorExited):
                self.handle_actor_exit(msg, sender)
        except Exception:
            handle_actor_system_fail()
