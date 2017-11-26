'''
This subscription pool obtains records in a queue sorted by the number of
records returned over time.  If an empty batch is pushed, the rate is
manipulated downward to 0.  The rate is pushed up on non-empty batch.  A
default rate is specifiable.

*Messages and Features*

Uses a typical rate of intake to judge how to organize the subscription queue. 

- Subscribe = Subscribe to the pool
- DeSubscribe = DeSubscribe from the pool
- Pull = Handle a pull request up to n batch size
- Push = Handle a push of a list based batch
- Cancel = Cancel a subscription in the pool, terminating the underlying actor.
- GetDropPolicy = Get the drop policy
- GetSubscribers = Get the current subscribers

Created on Nov 5, 2017

@author: aevans
'''

from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Pull, Push, Cancel, GetDropPolicy,\
    SetDefaultQueueFillRate
from reactive.streams.base_objects.subscription_pool import SubscriptionPool
from time import sleep
from reactive.message.router_messages import Subscribe, DeSubscribe
from reactive.message.stream_sub_pool_messages import GetSubscribers
import datetime


class SubscriptionRate():
    """
    The subscription rate
    """

    def __init__(self, subscription, rate):
        """
        Constructor

        :param subscription: The subscription
        :type subscription: Subscription
        :param rate: The current rate
        :type rate: int()
        """
        self.subscription = subscription
        self.rate = rate
        self.default_rate = rate
        self.__empty_batch_wait = .2
        self.__empty_times = 0


class RatedSubscriptionPool(SubscriptionPool):
    """
    Rated subscription pool
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__default_rate = 1
        self.__avail = []
        self.__waiting = []
        self.__empty_times = 0
        self.__empty_batch_wait = .005
        self.__refill_perc = .5
        self.__pull_on_empty = True
        self.__requests = 0
        self.__last_pull_time = datetime.datetime.now()

    def set_default_rate(self, msg, sender):
        """
        Sets the default rate value in the pool.

        :param msg:  The msg with the rate payload.
        :type msg: Message
        :param sender:  The sender
        :type sender:  BaseActor
        """
        self.__default_rate = msg.payload

    def subscribe(self, subscription):
        """
        Add a subscription

        :param subscription: The subscription
        :type subscription: Subscription
        """
        sbr = SubscriptionRate(subscription, self.__default_rate)
        self.__waiting.append(sbr)
        self.get_subscriptions().append(sbr)

    def remove_subscription(self, subscription):
        """
        Remove a subscription from the pool

        :param subscription: The subscription
        :type subscription: Subscription
        """
        found = []
        for sub in self.__avail:
            if sub.subscription == subscription:
                found.append(sub)
        if len(found) > 0:
            for sub in found:
                if sub in self.get_subscriptions():
                    self.get_subscriptions().remove(sub)
                self.__avail.remove(sub)

        found = []
        for sub in self.__waiting:
            if sub == subscription:
                if sub in self.get_subscriptions():
                    self.get_subscriptions().remove(sub)
                found.append(sub)
        if len(found) > 0:
            for sub in found:
                self.__waiting.remove(sub)

    def __remake_available(self):
        """
        Recreate the available subscription list
        """
        self.__avail = list(sorted(self.__waiting, key=lambda x: x.rate))
        self.__waiting = []

    def next(self, msg, sender):
        """
        Get the next batch

        :param msg: The message
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = []
        rq = self.get_result_q()
        pull_size = 0
        if rq.empty() is False:
            while rq.empty() is False and pull_size < batch_size:
                try:
                    val = rq.get_nowait()
                    batch.append(val)
                    pull_size += 1
                except Exception:
                    handle_actor_system_fail()
        msg = Push(batch, sender, self)
        self.send(sender, msg)
        self.check_pull()

    def check_pull(self):
        """
        Check to see if a pull is required.  Pull if required, setting the
        block pull to signal a request has been made.
        """
        rq = self.get_result_q()
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.get_default_q_size() - rq.qsize()
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        if (req_out < self.get_default_q_size() and\
        req_count >= self.get_max_batch_request_size()) or tdelt > 120:
            pull_size = self.get_default_q_size() - rq.qsize()
            pull_size = min([self.get_max_batch_request_size(), pull_size])
            if len(self.__avail) == 0:
                self.__remake_available()
            sub = self.__avail.pop(0)
            self.__waiting.append(sub)
            subscription = sub.subscription
            msg = Pull(pull_size, subscription, self.myAddress)
            self.send(subscription, msg)
            self.__requests += 1

    def handle_push(self, msg, sender):
        """
        Handle a push on the result queue.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        self.__requests -= 1
        batch = msg.payload
        rq = self.get_result_q()
        if isinstance(batch, list):
            if len(batch) > 0:
                for res in batch:
                    if self.get_result_q().full():
                        if self.__drop_policy == "pop":
                            try:
                                self.get_result_q().get_nowait()
                            except:
                                handle_actor_system_fail()
                    if rq.full() is False:
                        rq.put_nowait(res)
                sp = None
                for sub in self.get_subscriptions():
                    if sub.subscription == sender:
                        sp = sub
                if sp:
                    if len(batch) is 0:
                        sp.rate = max([sp.rate - 1, 0])
                    else:
                        sp.rate = min([sp.rate + 1, sp.default_rate])
                self.check_pull()
            else:
                self.__empty_times += 1
                if self.__empty_times >= len(self.get_subscriptions()):
                    self.__empty_times = 0
                    sleep(self.__empty_batch_wait)

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
                self.set_default_rate(msg, sender)
        except Exception:
            handle_actor_system_fail()
