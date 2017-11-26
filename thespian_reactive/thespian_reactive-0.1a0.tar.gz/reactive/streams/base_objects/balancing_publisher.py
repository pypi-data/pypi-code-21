'''
Publishers are attached to stages in a stream.  They handle demand from subscriptions.
These are special publishers to deal with the limitations of multi-processing and distribution.

A balancing publisher maintains a single queue.  This queue is used to publish
on request.

*Messages and Features*

Messages are pulled on request from a single queue

- Pull = Pull up to n messages from the buffer
- Push = Push the batch to the result queue (beware of the drop policy)
- SetPublisher = Set the message publisher
- SetDropPolicy = Set the drop policy for the router (pop or ignore)
- Subscribe = Subscribe to the publisher
- Desubscribe = Desubscribe from the publisher

Created on Nov 2, 2017

@author: aevans
'''

from reactive.streams.base_objects.publisher import Publisher
from reactive.structures.thread_queue import ReactiveQueue
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Pull, Push, SetDropPolicy,\
    SetPublisher, SetMaxBatchRequestSize, SetDefaultQueueFillRate
import datetime


class BalancingPublisher(Publisher):
    """
    Single queue balancing publisher
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__req_on_empty = False
        self.__requests = 0
        self.default_qsize = 1000
        self.queue = ReactiveQueue(maxsize=self.default_qsize)
        self.__drop_policy = "ignore"
        self.__publisher = None
        self.__q_fill_perc = .5
        self.__last_pull_time = datetime.datetime.now()

    def set_q_fill_perc(self, msg, sender):
        """
        Set the default q fill perc.

        :param msg:  The message with int payloads
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__q_fill_perc = msg.payload

    def set_drop_policy(self, msg, sender):
        """
        Sets the drop policy (pop or ignore).

        :param msg:  The message to handle with the policy payload
        :type msg: str()
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        payload = msg.payload
        if isinstance(payload, str):
            self.__drop_policy = payload

    def on_push(self, msg, sender):
        """
        Handle the push message.

        :param msg: The message to handle on push containing the list batch.
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        self.__requests -= 1
        payload = msg.payload
        if isinstance(payload, list):
            batch = self.queue.put_all_nowait(payload)
            if len(batch) > 0 and self.drop_policy == "pop":
                self.queue.get_all_nowait(len(batch))
                self.queue.put_all_nowait(batch)
                self.check_pull()

    def on_pull(self, msg, sender):
        """
        Handle a pull request. Up to n (int) results are pulled.

        :param msg: The message containing the n number of results to pull.
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = self.queue.get_n_nowait(batch_size)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.check_pull()
    
    def check_pull(self):
        rq = self.queue
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.default_qsize - rq.qsize()
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        if (req_out < self.default_qsize and\
        req_count >= self.get_max_batch_request_size()) or tdelt > 120:
            if self.__publisher:
                pull_size = self.get_max_batch_request_size()
                maxpull = self.default_qsize - rq.qsize()
                pull_size = min([maxpull, pull_size])
                if pull_size > 0:
                    msg = Pull(pull_size, self.__publisher, self.myAddress)
                    self.send(self.__publisher, msg)
                    self.__requests += 1

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
                self.on_pull(msg, sender)
            elif isinstance(msg, Push):
                self.on_push(msg, sender)
            elif isinstance(msg, SetPublisher):
                self.__publisher = msg.payload
            elif isinstance(msg, SetDropPolicy):
                self.set_drop_policy(msg, sender)
            elif isinstance(msg, SetMaxBatchRequestSize):
                self.set_max_batch_request_size(msg, sender)
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_q_fill_perc(msg, sender)
            else:
                super().receiveMessage(msg, sender)
        except Exception:
            handle_actor_system_fail()
