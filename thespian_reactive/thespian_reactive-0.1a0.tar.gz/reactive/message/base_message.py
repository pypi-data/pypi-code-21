'''
The base message implemented by all messages.

Created on Oct 29, 2017

@author: aevans
'''


class Message():

    def __init__(self, payload, target, sender):
        """
        Constructor

        :param payload:  The message payload
        :type payload:  object
        :param target:  The message target
        :type target:  BaseActor
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.payload = payload
        self.sender = sender
        self.target = target

    def __repr__(self, *args, **kwargs):
        """
        Return a string representation of the message.
        """
        rep = "{}(payload={}, target={}, sender={})"
        rep = rep.format(str(type(self)), self.payload, self.target, self.sender)
        return rep

    def __str__(self, *args, **kwargs):
        """
        Return a string representation of the message.
        """
        return self.__repr__()
