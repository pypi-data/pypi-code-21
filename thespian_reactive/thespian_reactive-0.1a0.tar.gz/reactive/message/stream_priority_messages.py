'''
Messages to set priorities in the stream.

Created on Nov 16, 2017

@author: aevans
'''
from reactive.message.base_message import Message


class SetPriorityQueueType(Message):
    """
    Sets the priority queue type.  Payload is PriorityQueueType
    """
    pass


class GetPriorityQueueType(Message):
    """
    Get the priority queue type.  Only for testing
    """
    pass
