'''
Created on Nov 13, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class SetQueueName(Message):
    """
    Set the queue name for handling the messages.  Payload is the name string. 
    """
    pass


class SetQueueExchange(Message):
    """
    Set the queue exchange.  Payload is the exchange name str().
    """
    pass


class ConnectToQueue(Message):
    """
    Sends a message to open a connection to the channel.
    """
    pass
