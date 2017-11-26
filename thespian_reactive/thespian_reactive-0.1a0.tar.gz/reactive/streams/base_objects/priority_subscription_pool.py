'''
Subscriptions in this pool are called on a priority basis, enabling some jobs
to take priority.

Created on Nov 5, 2017

@author: aevans
'''

from enum import Enum
from time import sleep
from reactive.streams.base_objects.subscription_pool import SubscriptionPool
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Pull, Push, Cancel,\
    SetDefaultQueueFillRate
from reactive.message.router_messages import DeSubscribe
from reactive.message.stream_sub_pool_messages import SubscribeWithPriority
import sys
from reactive.message.stream_priority_messages import GetPriorityQueueType,\
    SetPriorityQueueType
import datetime


class PriorityQueueType(Enum):
    MULTIQUEUE = 1
    EMPTY_RATED = 2


class SubscriptionPriority:
    """
    This class is handled by the priority subscription pool.  It creates a
    priority object.
    """

    def __init__(self, subscription, priority):
        """
        Constructor

        :param subscription: The subsription
        :type subscription: Subscription
        :param priority: The priority
        :type priority: int() 
        """
        self.subscription = subscription
        self.default_priority = priority
        self.priority = priority
        self.__empty_batch_wait = 2
        self.__empty_times = 0


class PrioritySubscriptionPool(SubscriptionPool):
    """
    Priority Subscription Pool that uses a priority object to sort calls to
    subscriptions. 
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__priority_queue = []
        self.__waiting_queue = []
        self.__queue_fill_perc = 0.5
        self.__current_index = 0
        self.__q_type = PriorityQueueType.EMPTY_RATED
        self.__requests = 0
        self.__empty_times = 0
        self.__last_pull_time = datetime.datetime.now()

    def set_priority_queue_type(self, msg, sender):
        """
        Set the priority queue type used by this actor.  This will reset
        a queue if the type is different.
        """
        self.__q_type = msg.payload
        self.remake_priority_queue()

    def get_priority_queue_type(self, msg, sender):
        """
        Return the priority queue type to the sender

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        msg = GetPriorityQueueType(self.__q_type, sender, self)
        self.send(sender, msg)
    
    def set_queue_fill_perc(self, msg, sender):
        """
        Set the default queue fill percentage.

        :param msg:  The message with the double payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__queue_fill_perc = msg.payload

    def remake_priority_queue(self):
        """
        Re-create the priority queue.  Sorts based on the priority.  
        """
        pq = self.get_subscriptions()
        subs = [x for x in pq]
        self.__priority_queue = list(sorted(subs, key=lambda x: x.priority))
        self.__waiting_queue = []

    def next(self, msg, sender):
        """
        Get the next n elements in the batch.

        :param msg: The message to handle.  Payload is the number of elements.
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
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
        self.check_pull(rq)
    
    def check_pull(self, rq):
        """
        Check the pull. Pull if necessary.

        :param rq:  Result Queue
        :type rq:  Queue
        """
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.get_default_q_size() - rq.qsize()
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        if (req_out < self.get_default_q_size() and\
        req_count >= self.get_max_batch_request_size()) or tdelt > 120:
            pull_size = self.get_max_batch_request_size()
            maxpull = self.get_default_q_size() - rq.qsize()
            pull_size = min([maxpull, pull_size])
            if len(self.__priority_queue) == 0:
                self.remake_priority_queue()
            sub = None
            if self.__q_type == PriorityQueueType.EMPTY_RATED:
                sub = self.__priority_queue.pop(0)
            elif self.__q_type == PriorityQueueType.MULTIQUEUE:
                sub = None
                submax = -1 *(sys.maxsize - 100)
                for res in self.__priority_queue:
                    if res.priority > submax:
                        sub = res
                        submax = res.priority
                    res.priority += 1
                if sub:
                    sub.priority = sub.default_priority
                    self.__priority_queue.remove(sub)
            if sub:
                outsub = sub.subscription
                self.__waiting_queue.append(sub)
                msg = Pull(pull_size, outsub, self.myAddress)
                self.send(outsub, msg)

    def handle_push(self, msg, sender):
        """
        Handle a push

        :param msg: The message.  Payload is the result batch list.
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        self.__requests -= 1
        payload = msg.payload
        if isinstance(payload, list):
            if len(payload) > 0:
                rq = self.get_result_q()
                for result in payload:
                    if rq.full():
                        if self.get_current_drop_policy() == "pop":
                            try:
                                rq.get_nowait()
                            except:
                                pass
                    if rq.full() is False:
                        rq.put_nowait(result)
                self.check_pull()
            else:
                self.__empty_times += 1
                subs = self.get_subscriptions()
                if self.__empty_times >= len(subs):
                    sleep(self.get_empty_batch_wait())
                    self.__empty_times = 0

    def subscribe(self, msg, sender):
        """
        Subscribe. If the subscription exists,
        reset the default priority.

        :param msg: The message to handle.  Payload is an actor.
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        subscription = msg.payload
        found = False
        i = 0
        sp = None
        while not found and i < len(self.get_subscriptions()):
            psp = self.get_subscriptions()[i]
            if psp.subscription == subscription:
                found = True
                sp = psp
            i += 1
        if sp:
            sp.priority = msg.default_priority
        else:
            sp = SubscriptionPriority(subscription, 0)
            subs  = self.get_subscriptions()
            subs.append(sp)
            subs = self.get_subscriptions()
            self.__waiting_queue.append(sp)

    def desubscribe(self, msg, sender):
        """
        DeSubscribe

        :param msg: The message to handle.  Payload is the actor.
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        subscription = msg.payload
        i = 0
        while i < len(self.get_subscriptions()):
            sp = self.__subscriptions
            if subscription == sp.subscription:
                i = len(self.get_subscriptions())
                self.get_subscriptions().remove(sp)

    def receiveMessage(self, msg, sender):
        """
        Handle message on receipt.

        :param msg: The message to handle.  Payload is the message.
        :type msg: Message
        :param sender: The sender
        :tpye sender: BaseActor
        """
        try:
            if isinstance(msg, SubscribeWithPriority):
                self.subscribe(msg, sender)
            elif isinstance(msg, DeSubscribe):
                self.remove_subscription(msg, sender)
            elif isinstance(msg, Pull):
                self.next(msg, sender)
            elif isinstance(msg, Push):
                self.handle_push(msg, sender)
            elif isinstance(msg, Cancel):
                sub = msg.payload
                self.cancel(sub)
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_queue_fill_perc(msg, sender)
            elif isinstance(msg, SetPriorityQueueType):
                self.set_priority_queue_type(msg, sender)
            elif isinstance(msg, GetPriorityQueueType):
                self.get_priority_queue_type(msg, sender)
            else:
                super().receiveMessage(msg, sender)
        except Exception:
            handle_actor_system_fail()
