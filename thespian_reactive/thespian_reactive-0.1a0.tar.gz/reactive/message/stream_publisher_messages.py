'''
Messages aimed specifically at stream publishers.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class PullBySubscription(Message):
    """
    This message submits a request to pull from a publisher by a subscription.
    """

    def __init__(self, payload, subscription, target, sender):
        """
        Constructor

        :param payload:  The subscription
        :type payload:  BaseActor
        :param subscription:   The subscription to handle
        :type subscription:  BaseActor
        :param target:  The target actor
        :type target:  BaseActor
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        super().__init__(payload, target, sender)
        self.subscription = subscription
