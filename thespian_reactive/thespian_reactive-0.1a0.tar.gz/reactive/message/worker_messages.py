'''
These messages are meant to target worker actors such as the TroupeStageActor.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class WorkLoad(Message):
    """
    Message sending a work load to an actor.  Payload is the workload list.
    """
    pass


class WorkResult(Message):
    """
    Message handling a work result.  Payload is the result batch list.
    """
    pass