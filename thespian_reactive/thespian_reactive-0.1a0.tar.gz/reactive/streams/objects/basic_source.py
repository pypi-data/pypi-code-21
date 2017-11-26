'''
A default source for pulling initial data. A source takes in data for usage in
the rest of the stream. Source extends base actor. 

Sources are publishers and inherit and expand on these messages.

*Messages and Features*

Sources receive requests from Subscription Pools and process them in turn.  The
source itself processes the request and so is not linked to a publisher.  The
source processes its own messages through  

- SetDropPolicy = Set the drop policy for the router (pop or ignore)
- Subscribe = Subscribe to the publisher.
- Desubscribe = Desubscribe from the publisher
- Pull = Pull records from the source with an int payload.


Created on Nov 2, 2017

@author: aevans
'''

from reactive.message.stream_messages import Pull, Push
from reactive.error.handler import handle_actor_system_fail
from reactive.streams.base_objects.publisher import Publisher
from reactive.streams.objects.source import SourceBase


class BasicSource(Publisher, SourceBase):

    def __init__(self):
        """
        Constructor
        """
        super(BasicSource, self).__init__()
        Publisher.__init__(self)
        SourceBase.setup(self)

    def do_pull(self, batch_size, msg, sender):
        """
        Overwrite this class to perform actions on receipt of a message.

        :param batch_size: Number of elments to pull
        :type batch_size: int
        :param msg: The message to handle with the batch_size payload.
        :type msg: Message
        :param sender: The message sender (not expected to be used here.
        :type sender: BaseActor
        """
        return None

    def pull(self, msg, sender):
        """
        Handle a pull from the source

        :param batch_size:  The size of the batch to pull
        :type batch_size:  int
        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = self.do_pull(batch_size, msg, sender)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.increment_pull()

    def receiveMessage(self, msg, sender):
        """
        Handle a message receipt.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        try:
            if isinstance(msg, Pull):
                self.pull(msg, sender)
            else:
                Publisher.receiveMessage(self, msg, sender)
                self.handle_message(msg, sender)
        except Exception:
            handle_actor_system_fail()
            self.increment_errors()
