'''
These messages are meant to be handled by a stream based subscription pool.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class SetDefaultSubscriptinRate(Message):
    """
    This message is used in the rated Subscription pool to set the default rate
    value.  The payload is an int.
    """
    pass


class SubscribeWithLogic(Message):
    """
    Subscribe to a stream component with a logic function (pickled).
    """

    def __init__(self, payload, logic, target, sender):
        """
        Constructor

        :param payload:  The actor to subscribe
        :type payload:  BaseActor
        :param logic:  The pickled logic function
        :type logic: bytearray
        """
        super().__init__(payload, target, sender)
        self.logic = logic


class SubscribeWithPriority(Message):
    """
    Subscribe to a subscription pool with a priority for 
    """

    def __init__(self, payload, priority, target, sender):
        """
        Constructor

        :param payload:   The actor to subscribe
        :type payload:  BaseActor
        :param priority:  The priority for the subscriber
        :type priority:  int
        :param target:  The target for the message
        :type target:  BaseActor
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        super().__init__(payload, target, sender)
        self.priority = priority


class ResetPriority(Message):
    """
    Reset the priority of a task in the subscription pool.
    """

    def __init__(self, payload, priority, target, sender):
        super().__init__(payload, target, sender)
        self.priority = priority


class SetSubscriber(Message):
    """
    Set the Subscriber with the payload as the Subscribe BaseActor.
    """
    pass


class GetSubscribers(Message):
    """
    Obtain the subscribers. 
    """
    pass
