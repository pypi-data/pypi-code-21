'''
Messages specific for a troupe based actor and supervisor.

Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class CreateActors(Message):
    """
    Create a set of actors in the troupe.  Payload is the number of actors.
    """
    pass


class RegisterTroupeKlass(Message):
    """
    Register the troupe class.  Payload is the class object.
    """
    pass


class TroupeWorkRequest(Message):
    """
    Handle a troupe work request
    """

    def __init__(self, payload, publisher, target, sender):
        super().__init__(payload, target, sender)
        self.publisher = publisher
