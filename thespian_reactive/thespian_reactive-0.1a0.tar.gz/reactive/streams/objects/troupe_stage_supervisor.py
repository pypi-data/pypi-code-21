'''
The troupe supervisor takes a troupe actor and ensures that the leader keeps
running.

*Messages and Features*

The troupe supervisor keeps the troupe from shutting down.  Troupes act like dynamic
routers.

- SetDefaultQueueFillRate = The default queue fill percentage.
- RegisterKlass = Register a class
- Pull = A pull message given to the troupe by the publisher or sink
- Push = Given by the subscription pool or pushing actor
- GetActorStatistics = Get statistics from the actor including number of pulls & etc.

Created on Nov 20, 2017

@author: aevans
'''

from datetime import datetime
from thespian.actors import ActorTypeDispatcher, ActorExitRequest
from reactive.message.stream_messages import Push, Pull
from reactive.structures.thread_queue import ReactiveQueue
from reactive.error.handler import handle_actor_system_fail


class TroupeStageSupervisor(ActorTypeDispatcher):
    """
    Troupe Stage Supervisor
    """

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__check_on_push = False
        self.__req_on_low = True
        self.__drop_policy = "ignore"
        self.__req_count = 0
        self.__fill_perc = 0.5
        self.__last_work_pull_time = datetime.now()
        self.__work_batch_size = 100
        self.__default_queue_fill_size = 1000
        self.__sub_pool = None
        self.__work_q = ReactiveQueue(maxsize=self.__default_queue_fill_size)
        self.__klass = None
        self.__request_on_push = True
        self.__pull = 0
        self.__max_batch_request_size = 100
        self.__troupe = None
        self.__last_pull_time = datetime.now()

    def receiveMsg_TearDown(self, msg, sender):
        """
        Tear down the supervisor

        :param msg:  The TearDown message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if self.__troupe:
            self.send(self.__troupe, ActorExitRequest())

    def receiveMsg_SetWorkBatchSize(self, msg, sender):
        """
        Set the work batch size.
    
        :param msg:  The message containing the int batch size
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__work_batch_size = msg.payload

    def receiveMsg_SetDropPolicy(self, msg, sender):
        """
        Set the drop policy

        :param msg:  The message to use
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__drop_policy = msg.payload

    def receiveMsg_SetSubscriptionPool(self, msg, sender):
        """
        Set the subscription pool

        :param msg:  The message to handle with the subscription pool payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__sub_pool = msg.payload

    def receiveMsg_SetMaxBatchRequestSize(self, msg, sender):
        """
        Set the maximum batch request size

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_request_size = msg.payload

    def receiveMsg_SetDefaultQueueFillRate(self, msg, sender):
        """
        Set the default queue fill rate.

        :param msg:  The message to handle.
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        payload = msg.payload
        self.__fill_perc = payload

    def receiveMsg_RegisterKlass(self, msg, sender):
        """
        Handle registration

        :param msg:  The message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__klass = msg.payload
        if self.__troupe:
            self.send(self.__troupe, ActorExitRequest())
        self.__troupe = self.createActor(self.__klass)

    def receiveMsg_ChildActorExited(self, msg, sender):
        """
        Handle a child actor on exit.  Restart the troupe.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if str(self.__troupe) == str(msg.childAddress) and self.__klass:
            self.__troupe = self.createActor(self.__klass)

    def check_pull(self):
        """
        Check whether we need to pull.
        """
        qperc = self.__default_queue_fill_size * self.__fill_perc
        qfill = self.__work_q.qsize()
        if qfill < qperc:
            self.__req_on_low = False
            pull_size = self.__default_queue_fill_size - self.__work_q.qsize()
            msg = Pull(pull_size, self.__sub_pool, self.myAddress)
            self.send(self.__sub_pool, msg)

    def receiveMsg_Pull(self, msg, sender):
        """
        Handle a pull message.

        :param msg:  The mesage to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            if self.__troupe:
                if msg.sender:
                    sender = msg.sender
                payload = msg.payload
                if isinstance(payload, int):
                    if self.__work_q.empty() is False:
                        remaining = payload
                        while remaining > 0 and self.__work_q.empty() is False:
                            batch_size = min([payload, self.__max_batch_request_size])
                            remaining = remaining - batch_size
                            batch = self.__work_q.get_n(batch_size)
                            if len(batch) > 0:
            
                                msg = Push(batch, self.__troupe, sender)
                                self.send(self.__troupe, msg)
                self.check_pull()
        except Exception:
            handle_actor_system_fail()

    def receiveMsg_Push(self, msg, sender):
        """
        Handle a push message.

        :param msg:  The mesage to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        try:
            self.__req_on_low = True
            payload = msg.payload
            if isinstance(payload, list) and len(payload) > 0:
                batch = self.__work_q.put_all_nowait(payload)
                if len(batch) > 0 and self.__drop_policy == "pop":
                    self.__work_q.get_n_nowait(len(batch))
                    self.__work_q.put_all_nowait(batch)
            if self.__check_on_push:
                self.check_pull()
        except Exception:
            handle_actor_system_fail()
