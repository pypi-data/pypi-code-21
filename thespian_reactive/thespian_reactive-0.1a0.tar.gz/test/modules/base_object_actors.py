'''
Standard actors for testing subscription pools and publishers.

Created on Nov 6, 2017

@author: aevans
'''

from random import Random
from reactive.actor.base_actor import BaseActor
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Push, Pull
from reactive.message.router_messages import Subscribe
from test.modules.object_work import get_work_batch_array


class SubTest(BaseActor):

    def __init__(self):
        super().__init__()
        self.results = []
        self.__subpool = None

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, Subscribe):
                payload = msg.payload
                self.__subpool = payload
            elif isinstance(msg, Pull):
                pool = self.__subpool
                payload_size = msg.payload
                psh = Push(self.results, sender, self.myAddress)
                self.send(sender, psh)
                self.results = []
                self.send(pool, Pull(payload_size, self.__subpool, self.myAddress))
            elif isinstance(msg, Push):
                payload = msg.payload
                self.results.extend(payload)
        except Exception:
            handle_actor_system_fail()


class PublisherRandActor(BaseActor):

    def __init__(self):
        super().__init__()

    def next(self, msg, sender):
        """
        Obtain the next batch

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = []
        for i in range(0, batch_size):
            str = Random().randint(0, 200)
            batch.append(str)
        msg = Push(batch, msg, self.myAddress)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        """
        Receive messages

        :param msg: The messgae to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        try:
            if isinstance(msg, Pull):
                self.next(msg, sender)
        except Exception:
            handle_actor_system_fail()

class PublisherStringActor(BaseActor):

    def __init__(self):
        super().__init__()

    def next(self, msg, sender):
        """
        Obtain the next batch

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = []
        for i in range(0, batch_size):
            str = "{}".format(self.myAddress)
            batch.append(str)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, Pull):
                self.next(msg, sender)
        except Exception:
            handle_actor_system_fail()

class PublisherArrayActor(BaseActor):

    def __init__(self):
        super().__init__()

    def next(self, msg, sender):
        """
        Obtain the next batch

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = get_work_batch_array()
        msg = Push(batch, msg, self.myAddress)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        try:
            if isinstance(msg, Pull):
                self.next(msg, sender)
        except Exception:
            handle_actor_system_fail()
