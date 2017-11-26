'''
A subscription pool is used to manage subscriptions and get work from a stream.
It manages multiple subscriptions.

*Messages and Features*

A basic subscription pool setup.

- Subscribe = Subscribe to the pool
- DeSubscribe = DeSubscribe from the pool
- Pull = Handle a pull request up to n batch size
- Push = Handle a push of a list based batch
- Cancel = Cancel a subscription in the pool, terminating the underlying actor.
- GetDropPolicy = Get the drop policy
- GetSubscribers = Get the current subscribers
- SetDefaultQueueFillRate = Set the default queue fill rate
- SetMaxBatchRequestSize = Set the default max batch request size

Created on Nov 1, 2017

@author: aevans
'''

from reactive.structures.thread_queue import Queue
from time import sleep

from reactive.actor.base_actor import BaseActor
from reactive.error.handler import handle_actor_system_fail
from reactive.message.router_messages import Subscribe, DeSubscribe
from reactive.message.stream_messages import Cancel, Pull, Push, GetDropPolicy,\
    SetDefaultQueueFillRate, SetMaxBatchRequestSize
from reactive.message.stream_sub_pool_messages import GetSubscribers


class SubscriptionPool(BaseActor):
    """
    Subscription pool containing subscriptions for an actor.
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__subscriptions = []
        self.__empty_batch_wait = .005
        self.__empty_times = 0
        self.__default_queue_size = 1000
        self.__result_q = Queue(maxsize=self.__default_queue_size)
        self.__drop_policy ="ignore"
        self.__refill_perc = .5
        self.__max_batch_request_size = 1000
        self.__pull_on_empty = True

    def get_empty_batch_wait(self):
        """
        Get the empty batch wait times.

        :return:  The empty batch wait times
        :rtype:  str
        """
        return self.__empty_batch_wait

    def get_current_drop_policy(self):
        """
        Return the current drop policy.

        :return:  The drop policy
        :rtype:  str
        """
        return self.__drop_policy

    def get_pull_on_empty(self):
        """
        Get whether to pull on empty

        :return: Whether to pull on empty
        :rtype: bool()
        """
        return self.__pull_on_empty

    def set_pull_on_empty(self, do_pull):
        """
        Set whether to pull on empty

        :param do_pull: Whether to pull on empty
        :type do_pull: bool()
        """
        self.__pull_on_empty = do_pull

    def get_max_batch_request_size(self):
        """
        Get the max batch request size.

        :return:  Return the max batch size
        :rtype:  int
        """
        return self.__max_batch_request_size

    def get_result_q(self):
        """
        Obtain the result queue

        :return:  The result queue
        :rtype:  Queue
        """
        return self.__result_q

    def get_default_q_size(self):
        """
        Return the default queue size

        :return: Get the default queue size
        :type: int()
        """
        return self.__default_queue_size

    def set_max_batch_request_size(self, msg, sender):
        """
        Set the maximum batch request size

        :param msg:  Message with int payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_request_size = msg.payload

    def set_refill_perc(self, msg, sender):
        """
        Set the queue refill fill percent.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__refill_perc = msg.payload

    def get_refill_perc(self):
        """
        Get the current refill perc.

        :return:  Get the refill percentage
        :rtype:  int
        """
        return self.__refill_perc

    def get_subscriptions(self):
        """
        Get the subscription
        :return: The current subscriptions
        :rtype: list()
        """
        return self.__subscriptions

    def set_drop_policy(self, msg, sender):
        """
        Set the drop policy

        :param msg: The message with the policy
        :type msg: Message
        :param sender: The message Sender
        :type sender: BaseActor
        """
        payload = msg.payload
        if isinstance(payload, str):
            if payload in ["pop", "ignore"]:
                self.__drop_policy = payload

    def get_drop_policy(self, msg, sender):
        """
        Get the drop policy

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        msg = GetDropPolicy(self.__drop_policy, sender, self)
        self.send(sender, msg)

    def subscribe(self, subscription):
        """
        Add a subscription to the pool.

        :param subscription: The subscription
        :type subscription: Subscription
        """
        if subscription not in self.__subscriptions:
            self.__subscriptions.append(subscription)

    def next(self, msg, sender):
        """
        The default subscription pool splits request sizes equally.

        :param msg: The message to handle.  Payload is batch size.
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = []
        rq = super().get_result_q()
        pull_size = 0
        if batch_size > 0:
            if rq.empty() is False:
                i = 0
                while rq.empty() is False and i < batch_size:
                    try:
                        pull_size += 1
                        val = rq.get_nowait()
                        batch.append(val)
                    except Exception:
                        handle_actor_system_fail()
                    finally:
                        i += 1
        msg = Push(batch, sender, self)
        self.send(sender, msg)
        self.check_pull()

    def check_pull(self):
        """
        Check to see if a pull is required.
        """
        subs = self.get_subscriptions()
        rq = self.__result_q
        qfill = int(self.__default_queue_size * self.__refill_perc)
        if rq.qsize() < qfill and len(subs) > 0 and self.__pull_on_empty:
            def_q_size = self.get_default_q_size() - rq.qsize()
            pull_size = int(def_q_size / len(subs))
            pull_size = min([self.__max_batch_request_size, pull_size])
            for sub in subs:
                msg = Pull(pull_size, sub, self.myAddress)
                self.send(sub, msg)
            self.__pull_on_empty = False

    def has_subscription(self, subscription):
        """
        Check whether a subscription is in the pool.
        """
        if subscription in self.__subscriptions:
            return True
        return False

    def remove_subscription(self, subscription):
        """
        Remove a subscription from the pool.
        """
        if self.has_subscription(subscription):
            self.__subscriptions.remove(subscription)

    def cancel(self, subscription):
        """
        Cancel and remove a subscription.

        :param subscription: The subscription to cancel and remove
        :type subscription: Subscription
        """
        if self.has_subscription(subscription):
            self.send(subscription, Cancel)
            self.remove_subscription(subscription)

    def handle_push(self, msg, sender):
        """
        Handle a push request to the queue.
        """
        self.__pull_on_empty = True
        batch = msg.payload
        if isinstance(batch, list):
            if len(batch) > 0:
                self.__empty_times = 0
                for result in batch:
                    if self.__result_q.full():
                        if self.__drop_policy == "pop":
                            try:
                                self.__result_q.get_nowait()
                            except Exception:
                                pass
                    if self.__result_q.full() is False:
                        self.__result_q.put_nowait(result)
            else:
                self.__empty_times += 1
                if self.__empty_times >= len(self.__subscriptions): 
                    twait = self.__empty_batch_wait
                    sleep(twait)
                    self.__empty_batch_wait = 0
                else:
                    if len(self.__subscriptions) > 0:
                        twait = self.__empty_batch_wait / len(self.__subscriptions)
                        sleep(twait)

    def get_subscribers(self, msg, sender):
        """
        Get the list of current subscribers

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        msg = GetSubscribers(self.__subscriptions, sender, self)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        """
        Handle message on receipt.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The sender
        :tpye sender: BaseActor
        """
        try:
            if isinstance(msg, Subscribe):
                sub = msg.payload
                self.subscribe(sub)
            elif isinstance(msg, DeSubscribe):
                sub = msg.payload
                self.remove_subscription(sub)
            elif isinstance(msg, Pull):
                self.next(msg, sender)
            elif isinstance(msg, Push):
                self.handle_push(msg, sender)
            elif isinstance(msg, Cancel):
                self.cancel(msg)
            elif isinstance(msg, GetDropPolicy):
                self.get_drop_policy(msg, sender)
            elif isinstance(msg, GetSubscribers):
                self.get_subscribers(msg, sender)
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_refill_perc(msg, sender)
            elif isinstance(msg, SetMaxBatchRequestSize):
                self.set_max_batch_request_size(msg, sender)
        except Exception:
            handle_actor_system_fail()
