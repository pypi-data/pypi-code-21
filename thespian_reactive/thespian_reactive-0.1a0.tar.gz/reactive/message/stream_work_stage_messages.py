'''
Messages sent to the work stage.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class TransientStageSettings(Message):
    """
    Transient stage settings.
    """

    def __init__(self, payload=None, min_count=None, max_count=None,
                 router_type=None, target=None, sender=None):
        """
        Transient settings.  All variables default to None

        :param payload:  router class, overwrites default 
        :type payload:  BaseActor
        :param min_count: Minimum number of router actors
        :type min_count: int
        :param max_count: Maximum number of router actors
        :type max_count: int
        :param target:  The target actor
        :type target:  BaseActor
        :param sender:  Message sender
        :type sender:  BaseActor
        """
        super().__init__(payload, target, sender)
        self.min_count = min_count
        self.max_count = max_count
        self.router_type = router_type

class GetActorStatistics(Message):
    """
    Get statistics related to the dynamic creation and deletion of actors
    """
    pass

class RequestWork(Message):
    """
    Set to request more work
    """
    pass


class SetSubscriptionPool(Message):
    """
    Set the Subscription Pool in a work stage.  Payload is the subscription
    pool.
    """
    pass


class SetWorkBatchSize(Message):
    """
    Set the work batch size.  Payload is int.
    """
    pass


class CreateWorkerProcess(Message):
    """
    Create a worker process.  Payload is the function reference.  Generally,
    not always, a worker process takes msg (Message) and sender (BaseActor).
    """
    pass
