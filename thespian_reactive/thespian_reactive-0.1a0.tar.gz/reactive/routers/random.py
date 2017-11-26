'''
Random Router. This router randomly chooses an actor to push to.
Routers are somewhat inefficient in that RouteTell and RouteAsk
must be used to avoid as much blocking as possible. This will
improve throughput but add a small dose of complexity.

To ask, call ask to block and wait for a return and use RouteAsk.
To tell, call tell and use RouteTell. 

This will cause the ActorRoutee actors to performing the correct
behavior.

*Messages and Features*

Messages are routed to routees randomly.

- Subscribe = Subscribe an actor to this pubsub
- Desubscribe = Desubscribe from this pubsub
- RouteAsk = Route an ask request to this pubsub
- Broadcast = Broadcast a message to all actors in this router
- GetNumRoutees = Get the number of routees in this actor
- RegisterKlass = Register the router class
- CreateActors = Create a number of actors (after registering the router class)

Created on Oct 29, 2017

@author: aevans
'''

from random import Random

from reactive.error.handler import handle_actor_system_fail
from reactive.message.router_messages import RouteTell, RouteAsk, Subscribe, \
    DeSubscribe, Broadcast, GetNumRoutees
from reactive.routers.pub_sub import PubSub
from thespian.actors import ChildActorExited
from reactive.message.stream_messages import RegisterKlass
from reactive.message.troupe_messages import CreateActors


class RandomRouter(PubSub):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()

    def handle_message(self, msg, sender):
        """
        Handle a tell request.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        actor = Random().choice(self.get_actor_set())
        self.send(actor, msg)

    def receiveMessage(self, msg, sender):
        """
        Handle the incoming messages

        :param msg: The incoming message
        :type msg: Message()
        :param sender: The sender
        :type sender: Actor 
        """
        try:
            self.check_message_and_sender(msg, sender)
            if isinstance(msg, Subscribe):
                self.handle_subscription(msg, sender)
            elif isinstance(msg, RouteAsk) or isinstance(msg, RouteTell):
                self.handle_message(msg, sender)
            elif isinstance(msg, DeSubscribe):
                self.handle_desubscribe(msg, sender)
            elif isinstance(msg, Broadcast):
                self.handle_broadcast(msg, sender)
            elif isinstance(msg, GetNumRoutees):
                self.handle_get_num_actors(msg, sender)
            elif isinstance(msg, ChildActorExited):
                self.handle_actor_exited(msg, sender)
            elif isinstance(msg, RegisterKlass):
                self.set_router_klass(msg, sender)
            elif isinstance(msg, CreateActors):
                self.create_actors(msg, sender)
            else:
                self.handle_unexpected_message(msg, sender)
        except:
            handle_actor_system_fail()
