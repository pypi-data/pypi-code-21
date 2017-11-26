'''
Implements SubscriptionPool but uses round robin on subscriptions when calling
get_next.  This subscription pool calls subscriptions in a round robin fashion.

*Messages and Features*

Sends requests to publishers in a round robin fashion.

- Subscribe = Subscribe to the pool
- DeSubscribe = DeSubscribe from the pool
- Pull = Handle a pull request up to n batch size
- Push = Handle a push of a list based batch
- Cancel = Cancel a subscription in the pool, terminating the underlying actor.
- GetDropPolicy = Get the drop policy
- GetSubscribers = Get the current subscribers

Created on Nov 1, 2017

@author: aevans
'''

from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import Pull, Push
from reactive.streams.base_objects.subscription_pool import SubscriptionPool
import datetime


class RoundRobinSubscriptionPool(SubscriptionPool):
    """
    Round robin based subscription pool.
    """
        
    def __init__(self):
        """
        Constructor

        :param drop_policy: Specify how to handle queue overfill
        :type drop_policy: str()
        """
        super().__init__()
        self.__index = 0
        self.__last_pull_time = datetime.datetime.now()
        self.__requests = 0

    def handle_push(self, msg, sender):
        """
        Handle the push and decrement requests.

        :param msg:  Push message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__requests -= 1
        super().handle_push(msg, sender)
        

    def next(self, msg, sender):
        """
        Get the next n elements in the batch.

        :param msg: The message to handle
        :type msg: Message
        :param sender: The message sender
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
        self.check_pull()

    def check_pull(self):
        """
        Check if a pull needs to be performed.  Pull as necessary.
        """
        subs = self.get_subscriptions()
        rq = self.get_result_q()
        req_out = self.__requests * self.get_max_batch_request_size()
        req_count = self.get_default_q_size() - rq.qsize()
        tdelt = datetime.datetime.now() - self.__last_pull_time
        tdelt = tdelt.total_seconds()
        mbs = self.get_max_batch_request_size()
        if (req_out < self.get_default_q_size() and\
        req_count >= self.get_max_batch_request_size()) or tdelt > 120:
            if subs and len(subs) > 0:
                if self.__index >= len(subs):
                    self.__index = 0
                sub = subs[self.__index]
                self.__index += 1
                pull_size = self.get_default_q_size() - rq.qsize()
                pull_size = min([pull_size, mbs])
                msg = Pull(pull_size, sub, self.myAddress)
                self.send(sub, msg)
                self.__requests += 1
