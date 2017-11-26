'''
A set of messages for the router enterprise data patterns.

Created on Oct 29, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class RouteTell(Message):
    """
    Route a tell request through a non-balancing router.
    """
    pass


class RouteAsk(Message):
    """
    Route an ask request through a non-balancing router.
    """

    def __init__(self, payload, target, sender, timeout=None):
        super().__init__(payload, target, sender)
        self.timeout = timeout

class BalancingAsk(RouteAsk):
    """
    Handle an ask request to a balancing router.
    """

    def __init__(self, router, msg):
        super().__init__(msg.payload, msg.target, msg.sender)
        if isinstance(msg, RouteAsk):
            super().timeout = msg.timeout
        self.router = router

class BalancingTell(RouteTell):
    """
    Handle a tell request through a non-balancing router
    """

    def __init__(self, router, msg):
        super().__init__(msg.payload, msg.target, msg.sender)
        self.router = router

class Broadcast(Message):
    """
    Broadcast to all router members
    """
    pass


class Subscribe(Message):
    """
    Subscribe to the router
    """
    pass


class DeSubscribe(Message):
    """
    DeSubscribe from the router.
    """
    pass


class GetNumRoutees(Message):
    """
    Mostly for testing purposes.  Get the number of routees at a specific time.
    """
    pass
