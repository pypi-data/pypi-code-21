'''
Subscription sends requests for information. It takes an actor to send to
as a reference and passes batch requests to it via Pull(n, rec, sender).
This is both a subscriber and a subscription per the reactive streams
model. Not buying into the idea of have one subscription and a separate
subscriber.

*Messages and Features*

- Pull = Pull from the subscription buffer up to a batch of n
- Push = Push to the subscription buffer a list batch
- SetPublisher = Set the subscriptions publisher. Allowed once.
- SetDropPolicy = Set the drop policy
- GetDropPolicy = Get the current drop policy
- SetSubscriber = Set the subscriber making demand requests. Allowed Once.
- Peek = Return the first element in the buffer or None
- Cancel = Cancel the subscription and its underlying actor

Created on Nov 1, 2017

@author: aevans
'''

import logging
from queue import Queue
from thespian.actors import ActorExitRequest

from reactive.actor.base_actor import BaseActor
from reactive.actor.state import ActorState
from reactive.error.handler import handle_actor_system_fail
from reactive.message.router_messages import Subscribe
from reactive.message.stream_messages import Pull, Cancel, Push, SetDropPolicy,\
    GetDropPolicy, Peek, SetPublisher, SetDefaultQueueFillRate
from reactive.message.stream_sub_pool_messages import SetSubscriber


class Subscription(BaseActor):
    """
    Subscription router
    """

    def __init__(self):
        """
        Constructor

        :param subscriber: The subscriber actor
        :type subscriber: BaseActor
        :param drop_policy: Policy to take if the results queue
        :type drop_policy
        """
        super().__init__()
        self.__pull_on_empty = True
        self.__default_q_size = 1000
        self.__fill_perc = .5
        self.__result_q = Queue(maxsize=self.__default_q_size)
        self.__publisher = None
        self.__subscribed = False
        self.__drop_policy = "ignore"

    def set_queue_fill_perc(self, msg, sender):
        """
        Set the queue fill rate usd to determine when requests are made.

        :param msg:  The message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__fill_perc = msg.payload

    def set_drop_policy(self, msg, sender):
        """
        Set the drop policy.

        :param msg: The message containing the policy
        :type msg: Message
        :param sender: The sender
        """
        payload = msg.payload
        if isinstance(payload, str):
            if payload.strip().lower() in ["pop", "ignore"]:
                self.__drop_policy = payload

    def get_drop_policy(self, msg, sender):
        """
        Get the current drop policy.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: Sender
        """
        msg = GetDropPolicy(self.__drop_policy, sender, self)
        self.send(sender, msg)

    def set_publisher(self, msg, sender):
        """
        Set the subscriber

        :param msg: The message with the subscriber
        :type msg: Message
        :param sender: The subscription sender
        :type sender: BaseActor
        """
        payload = msg.payload
        self.__publisher = payload

    def request(self, batch_size, sender):
        """
        Send out a request for a batch of work

        :param batch_size: The batch size
        :type batch_size: int()
        :param sender: The sender of the original message
        :type sender: BaseActor
        """
        rec = self.__publisher
        addr = self.myAddress
        msg = Pull(batch_size, sender, addr)
        self.send(rec, msg)

    def on_next(self, msg, sender):
        """
        On the next request, call request

        :param batch_size: The batch size
        :type batch_size: int()
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        pull_size = 0
        batch = []
        batch_size = msg.payload
        if msg.sender:
            sender = msg.sender
        rq = self.__result_q
        if rq.empty() is False:
            while pull_size < batch_size and rq.empty() is False:
                val = rq.get_nowait()
                batch.append(val)
                pull_size += 1
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        qfill = self.__default_q_size - rq.qsize()
        minfill = int(self.__default_q_size * self.__fill_perc)
        if qfill < minfill and self.__pull_on_empty:
            pull_size = self.__default_q_size - rq.qsize()
            self.request(pull_size, sender)
            self.__pull_on_empty = False
        elif rq.empty() and self.__pull_on_empty:
            self.request(batch_size, sender)
            self.__pull_on_empty = False

    def handle_batch(self, msg):
        """
        Handle a batch of results.

        :param msg: The message to handle
        :type msg: Message
        """
        self.__pull_on_empty = True
        batch = msg.payload
        rq = self.__result_q
        if isinstance(batch, list):
            if len(batch) > 0:
                for result in batch:
                    if rq.full():
                        if self.__drop_policy == "pop":
                            try:
                                rq.get_nowait()
                            except Exception:
                                pass
                    if rq.full() is False:
                        rq.put_nowait(result)

    def cancel(self):
        """
        Set the state to down. Kill the actor with ActorExitRequest
        """
        self.on_complete()
        self.send(self, ActorExitRequest())
        self.state = ActorState.TERMINATED

    def on_subscribe(self, msg, sender):
        """
        This subscribes to a publisher. Only one publisher is allowed.

        :param msg: The sending message
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        if self.__subscribed is False:
            pub = msg.payload
            if isinstance(pub, BaseActor):
                Subscribe(self.__publisher, pub, self.myAddress)
                self.send(pub, msg)
                self.__subscribed = True

    def on_complete(self):
        """
        User implemented. Called on Cancel. Will not be called
        on a different form of error that causes catastrophic
        failure.
        """
        logging.info("Actor Completing {}".format(str(self)))

    def peek(self, msg, sender):
        """
        For testing purposes, allows to peek in the queue

        :param msg: The peek message
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        payload = msg.payload
        if msg.sender:
            sender = msg.sender
        batch = []
        if isinstance(payload, int):
            if self.__result_q.empty() is False:
                i = 0
                while i < payload and self.__result_q.empty() is False:
                    i += 1
                    val = self.__result_q.get_nowait()
                    batch.append(val)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        """
        Handle a message on receipt. The message sender is used to
        receive the results of any additional request

        :param msg: The message received
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        try:
            if isinstance(msg, Pull):
                self.on_next(msg, sender)
            elif isinstance(msg, Push):
                self.handle_batch(msg)
            elif isinstance(msg, SetPublisher):
                self.set_publisher(msg, sender)
            elif isinstance(msg, SetSubscriber):
                self.set_publisher(msg, sender)
            elif isinstance(msg, SetDropPolicy):
                self.set_drop_policy(msg, sender)
            elif isinstance(msg, GetDropPolicy):
                self.get_drop_policy(msg, sender)
            elif isinstance(msg, Peek):
                self.peek(msg, sender)
            elif isinstance(msg, Cancel):
                self.cancel()
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_queue_fill_perc(msg, sender)
        except Exception:
            handle_actor_system_fail()
