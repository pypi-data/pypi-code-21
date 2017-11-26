'''
Maintains multiple queues which are published to. Back pressure occurs
by taking the min of all of the queues being filled.

*Messages and Features*

This publisher obtains up to n results from the publisher queue stored under
the sender address, an addrss pre-subscribed to the publisher. 

- Pull = Pull up to n messages from the buffer
- Push = Push the batch to the result queue (beware of the drop policy)
- SetPublisher = Set the message publisher
- SetDropPolicy = Set the drop policy for the router (pop or ignore)
- Subscribe = Subscribe to the publisher.
- Desubscribe = Desubscribe from the publisher

Created on Nov 2, 2017

@author: aevans
'''

from reactive.structures.thread_queue import ReactiveQueue
from random import Random
from reactive.streams.base_objects.publisher import Publisher
from reactive.error.handler import handle_actor_system_fail
from reactive.routers.router_type import RouterType
from reactive.message.stream_messages import Push, Pull, SetDropPolicy,\
SetDefaultQueueFillRate
from reactive.message.stream_sub_pool_messages import SetSubscriber
import datetime

class MultiQPublisher(Publisher):
    """
    A multi queue publisher maintaining a queue per publisher.
    """

    def __init__(self):
        super().__init__()
        self.__req_on_empty = False
        self.__queues = {}
        self.__default_q_size = 1000
        self.__max_pull_wait = 120
        self.__router_type = RouterType.BROADCAST
        self.__current_index = 0
        self.__max_size = 0
        self.__fill_perc = .5
        self.__pull_on_empty = True
        self.__last_pull_time = datetime.datetime.now()
        self.__requests = 0

    def set_max_fill_perc(self, msg, sender):
        """
        Set the maximum fill percentage.

        :param msg:  The message with a double payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__fill_perc = msg.payload

    def set_router_type(self, msg, sender):
        """
        Set the router type

        :param msg: The message to handle with router type payload.
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        payload = msg.payload
        self.__router_type = payload

    def get_max_queue_size(self):
        """
        Get the maximum queue size

        :return:  The largest queue size
        :rtype:  int
        """
        max_size = 0
        for k,q in self.__queues.items():
            max_size = max([max_size, q.qsize()])
        return max_size

    def on_push(self, msg, sender):
        """
        Handle a push request.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The sender
        :type sender BaseActor
        """
        self.__requests -= 1
        payload = msg.payload
        if self.__router_type == RouterType.BROADCAST:
            for k,v in self.__queues.items():
                batch = v.put_all_nowait(payload)
                if len(batch) > 0 and self.__drop_policy == "pop":
                    v.get_n_nowait(len(batch))
                    v.put_n_nowait(batch)
        elif self.__router_type == RouterType.ROUND_ROBIN:
            keys = list(sorted(self.__queues.keys()))
            key = keys[self.__current_index]
            rq = self.__queues[key]
            batch = rq.put_all_nowait(payload)
            if len(batch) > 0 and self.drop_policy == "pop":
                rq.get_n_nowait(len(batch))
                rq.put_all_nowait(batch)
            if len(payload) > 0:
                self.check_pull(rq)
        elif self.__router_type == RouterType.RANDOM:
            keys = list(sorted(self.__queues.keys()))
            k = Random().choice(keys)
            rq = self.__queues[rq]
            batch = rq.put_all_nowait(payload)
            if len(batch) > 0 and self.drop_policy == "pop":
                rq.get_n_nowait(len(batch))
                rq.put_n_nowait(batch)
            if len(payload) > 0:
                self.check_pull(rq)

    def contains_addr(self, addr):
        """
        Find whether the address is contained in the map

        :param addr: The address
        :type addr: ActorAddress
        :return: Whether the queue map has the address
        :rtype: bool
        """
        for sub in self.__queues.keys():
            if addr == sub:
                return True
        return False

    def on_pull(self, msg, sender):
        """
        Handle a pull message.

        :param msg: The Message to handle
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        batch_size = msg.payload
        batch = []
        pull_size = 0
        if msg.sender:
            sender = msg.sender
        rq = None
        if self.contains_addr(sender.addressDetails):
            rq = self.__queues[sender.addressDetails]
            if isinstance(batch_size, int):
                if batch_size > 0:
                    batch = rq.get_n_nowait(batch_size)
        self.__max_size = self.get_max_queue_size()
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.check_pull(rq)

    def check_pull(self, rq):
        """
        Check pull and request if necessary.

        :param rq:  The current queue
        :type rq:  Queue
        """
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.__default_q_size - rq.qsize()
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        mbs = self.get_max_batch_request_size()
        max_pull = self.__max_pull_wait
        if (req_out < self.__default_q_size and\
        req_count >= self.get_max_batch_request_size()) or tdelt > max_pull:
            pull_size = self.__default_q_size - self.__max_size
            pull_size = min([mbs, pull_size])
            msg = Pull(pull_size, self.get_publisher(), self.myAddress)
            self.send(self.get_publisher(), msg)
            self.__last_pull_time = datetime.datetime.now()
            self.__requests += 1

    def subscribe(self, msg, sender):
        """
        Add a subscription and queue.
        """
        subscription = msg.payload
        if subscription:
            if subscription.addressDetails not in self.__queues:
                self.__queues[subscription.addressDetails] = ReactiveQueue(
                    maxsize=self.__default_q_size)

    def receiveMessage(self, msg, sender):
        """
        Handle a message receipt.

        :param msg:  The message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            if isinstance(msg, Pull):
                self.on_pull(msg, sender)
            elif isinstance(msg, Push):
                self.on_push(msg, sender)
            elif isinstance(msg, SetSubscriber):
                self.subscribe(msg, sender)
            elif isinstance(msg, SetDropPolicy):
                self.set_drop_policy(msg, sender)
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_max_fill_perc(msg, sender)
            else:
                super().receiveMessage(msg, sender)
        except Exception:
            handle_actor_system_fail()
