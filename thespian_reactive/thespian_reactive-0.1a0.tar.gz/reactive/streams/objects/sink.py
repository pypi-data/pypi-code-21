'''
This sink uses the priority subscription pool to ask for work and a secondary
actor for pushing.  The user must implement and provide a sink actor.

Created on Nov 17, 2017

@author: aevans
'''

from thespian.actors import ActorTypeDispatcher
from reactive.message.stream_messages import Pull, Push
from _datetime import datetime
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_sink_messages import GetLastPushTime
import sys
from reactive.structures.thread_queue import ReactiveQueue


class BaseSink(ActorTypeDispatcher):
    """
    Rated subscription pool
    """

    def __init__(self):
        """
        Constructor
        """
        super(BaseSink, self).__init__()
        self.__last_push = datetime.now()
        self.__work_q = ReactiveQueue()
        self.__drop_policy = "ignore"
        self.__req_count = 0
        self.__sink_procs = []
        self.__klass = None
        self.__fill_perc = 0.5
        self.__default_qsize = 1000
        self.__max_batch_size = 100
        self.__sub_pool = None

    def receiveMsg_SetDropPolicy(self, msg, sender):
        """
        Set the drop policy for the sink.

        :param msg:  The message containing the drop policy
        :type msg:  Message
        :param sender:   The message sender
        :type sender:  BaseActor
        """
        self.__drop_policy = msg.payload

    def receiveMsg_TearDown(self, msg, sender):
        """
        Close out all remaining processes.

        :param msg:  The TearDown message
        :type msg:  Message
        :param sender:   The message sender
        :type sender:  BaseActor
        """
        with self.__do_terminate:
            self.__do_terminate.value = True
        
        if len(self.__sink_procs) > 0:
            for proc in self.__sink_procs:
                try:
                    proc.join()
                except Exception as e:
                    handle_actor_system_fail()

    def receiveMsg_SetMaxBatchRequestSize(self, msg, sender):
        """
        Set the maximum batch request size.

        :param msg: The message to handle with the batch size int
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_size = msg.payload

    def receiveMsg_SetSubscriptionPool(self, msg, sender):
        """
        Set the subscription pool.

        :param msg:  The message containing the subscription
        :type msg:  Message
        :param sender:  The message sender
        :tpye sender:  BaseActor
        """
        self.__sub_pool = msg.payload

    def receiveMsg_RegisterKlass(self, msg, sender):
        """
        Handle class registration.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__klass = msg.payload

    def receiveMsg_GetLastPushTime(self, msg, sender):
        """
        Send back the last push time.

        :param msg:  The GetLastPushTime message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor  
        """
        if msg.sender:
            sender = msg.sender
        msg = GetLastPushTime(self.__last_push, sender, self.myAddress)
        self.send(sender, msg)


    def receiveMsg_Start(self, msg, sender):
        """
        Handle the start message.

        :param msg:  The message signalling a start
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if self.__is_started is False:
            rc = self.__req_count * self.__max_batch_size
            while rc < self.__default_qsize:
                msg = Pull(
                    self.__max_batch_size, self.__sub_pool, self.myAddress)
                self.send(self.__sub_pool, msg)
                self.__req_count += 1
                rc = self.__req_count * self.__max_batch_size

    def check_pull(self):
        """
        Check whether a pull request should be made
        """
        qfill = self.__work_q.qsize()
        qperc = self.__default_qsize * self.__fill_perc
        mrs = self.__req_count * self.__max_batch_size
        while qfill <= qperc and mrs < self.__default_qsize:
            pull_size = self.__default_qsize - self.__work_q.qsize()
            pull_size = min([pull_size, self.__max_batch_size])
            msg = Pull(pull_size, self.__sub_pool, self.myAddress)
            self.send(self.__sub_pool, msg)
            self.__req_count += 1
            mrs = self.__req_count * self.__max_batch_size

    def receiveMsg_Pull(self, msg, sender):
        """
        Handle the pull message from a sink actor.

        :param msg:  The message signalling a start
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        batch_size = msg.payload
        if msg.sender:
            sender = msg.sender
        batch = self.__work_q.get_n_nowait(batch_size)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.check_pull()

    def receiveMsg_Push(self, msg, sender):
        """
        Handle a push of records to the sink

        :param msg:  The message with the batch payload
        :type msg:  Message
        :param sender:   The message sender
        :type sender:  BaseActor
        """
        batch = msg.payload
        if isinstance(batch, list):
            batch = self.__work_q.put_all_nowait(batch)
            if len(batch) > 0 and self.__drop_policy == "pop":
                self.__work_q.get_n_nowait(len(batch))
                batch = self.__work_q.put_all_nowait(batch)
