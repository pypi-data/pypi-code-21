'''
A Logic processor stores a queue per condition. A default base queue is
supported as well.

*Messages and Features*

Messages are pulled by queues stored under the logic function up to n results.

- Pull = Pull up to n messages from the buffer
- Push = Push the batch to the result queue (beware of the drop policy)
- SetPublisher = Set the message publisher
- SetDropPolicy = Set the drop policy for the router (pop or ignore)
- SubscribeWithLogic = Subscribe to the publisher with a pickled logic function
- Desubscribe = Desubscribe from the publisherr
- GetPublisher = Return the publisher
- GetSubscribers = Get the subscribers

Created on Nov 2, 2017

@author: aevans
'''

import base64
import dill
from reactive.streams.base_objects.publisher import Publisher
from reactive.structures.thread_queue import ReactiveQueue
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Push, SetPublisher, Pull,\
    GetPublisher, SetDefaultQueueFillRate
from reactive.message.router_messages import DeSubscribe
from reactive.message.stream_sub_pool_messages import GetSubscribers,\
    SubscribeWithLogic
import datetime

class LogicPublisher(Publisher):
    """
    Publisher that connects a subscriptions to their outputs. 
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__max_pull_wait = 120
        self.__last_pull_time = datetime.datetime.now()
        self.__req_on_empty = True
        self.__pull_on_empty = True
        self.__max_size = 0
        self.__default_q_size = 1000
        self.__fill_perc = 0.5
        self.__publisher = None
        self.__total_size = 0
        self.__requests = 0
        self.__subscriptions = {}
        self.__queues = {
            'default' : ReactiveQueue()
        }

    def set_max_pull_wait(self, msg, sender):
        """
        Set the maximum time to wait before pulling data.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_pull_wait = msg.payload

    def set_default_fill_perc(self, msg, sender):
        """
        Set the default queue rate.

        :param msg:  The message payload of double
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__fill_perc = msg.payload

    def get_subscriber(self, val):
        """
        Go through subscribers until finding a subscriber where
        the resulting logic is True

        :param val: The value to check against
        :type val: The value
        :return: The value to check for a subscription with or None
        :rtype: Subscription
        """
        if self.__subscriptions:
            for k,v in self.__subscriptions.items():
                if v(val):
                    return k
        return None

    def get_max_size(self):
        """
        Get the current queue max size.

        :return:  Maximum queue size
        :rtype: int
        """
        max_size = 0
        for k,q in self.__queues.items():
            if q.qsize() > max_size:
                max_size = max([max_size, q.qsize()])
        return max_size

    def on_push(self, msg, sender):
        """
        Handle a push message

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        self.__requests -= 1
        if msg.sender:
            sender = msg.sender
        payload = msg.payload
        if isinstance(payload, list):
            if len(payload) > 0:
                self.__req_on_empty = True
                for result in payload:
                    sub = self.get_subscriber(result)
                    if sub:
                        if sub in self.__queues.keys():
                            rq = self.__queues[sub]
                            if rq.full():
                                if self.drop_policy == "pop":
                                    try:
                                        rq.get_nowait()
                                    except:
                                        pass
                            if rq.full() is False:
                                rq.put_nowait(result)

    def next(self, msg, sender):
        """
        Handle a pull request

        :param msg: The message to handle
        :type msg: Message
        :param sender: The sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        subscription = sender
        batch_size = msg.payload
        batch = []
        rq = None
        if subscription.addressDetails in self.__queues.keys():
            rq = self.__queues[subscription.addressDetails]
            if rq.empty() is False:
                batch = rq.get_n(batch_size)
        self.__max_size = self.get_max_size()
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.check_pull()

    def check_pull(self):
        """
        Check whether a pull should be made.  Perform pull.
        """
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.__default_q_size - self.__max_size
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        if (req_out < self.__default_q_size and\
        req_count >= self.get_max_batch_request_size()) or tdelt > 120:
            if self.get_publisher():
                self.__last_pull_time = datetime.datetime.now()
                self.__requests += 1
                pub = self.get_publisher()
                pull_size = self.get_max_batch_request_size()
                maxpull = self.__default_q_size - self.__max_size
                pull_size = min([maxpull, pull_size])
                if pull_size > 0:
                    msg = Pull(pull_size, pub, self.myAddress)
                    self.send(pub, msg)

    def get_subscribers(self, msg, sender):
        """
        Get the subscribers

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        gsm = GetSubscribers(self.__subscriptions, sender, self)
        self.send(sender, gsm)

    def subscribe(self, msg, sender):
        """
        Subscribe to the queues

        :param subscription: The subscription request
        :type subscription: Subscription
        """
        subscription = msg.payload
        sub_addr = subscription.addressDetails
        logic = msg.logic
        dec = base64.b64decode(logic)
        logic_f = dill.loads(dec)
        if sub_addr not in self.__subscriptions.keys():
            self.__subscriptions[sub_addr] = logic_f
            self.__queues[sub_addr] = ReactiveQueue(maxsize = self.__default_q_size)

    def desubscribe(self, msg, sender):
        """
        DeSubscribe from the queues

        :param subscription: The subscription
        :type subscription: Subscription
        """
        subscription = msg.payload
        sub_addr = subscription.addressDetails
        if sub_addr in self.__subscriptions.keys():
            self.__subscriptions.pop(sub_addr)
        if sub_addr in self.__queues.keys():
            self.__queues.pop(sub_addr)

    def get_publisher_callback(self, msg, sender):
        """
        Get a publisher

        :param msg: The message
        :type msg: Message
        :param sender: The sender of the message
        :type sender: BaseActor
        """
        if msg.sender:
            sender = msg.sender
        pub = self.get_publisher()
        msg = GetPublisher(pub, sender, self)
        self.send(sender, msg)

    def receiveMessage(self, msg, sender):
        """
        Handle a message.

        :param msg: Handle a receive message
        :type msg: Message
        :param sender: The message sender
        :type sender: BaseActor
        """
        try:
            if isinstance(msg, Pull):
                self.next(msg, sender)
            elif isinstance(msg, Push):
                self.on_push(msg, sender)
            elif isinstance(msg, SetPublisher):
                self.set_publisher(msg, sender)
            elif isinstance(msg, SubscribeWithLogic):
                self.subscribe(msg, sender)
            elif isinstance(msg, DeSubscribe):
                self.desubscribe(msg, sender)
            elif isinstance(msg, GetSubscribers):
                self.get_subscribers(msg, sender)
            elif isinstance(msg, GetPublisher):
                self.get_publisher_callback(msg, sender)
            elif isinstance(msg, SetDefaultQueueFillRate):
                self.set_default_fill_perc(msg, sender)
        except Exception:
            handle_actor_system_fail()
