'''
Troupe or regularly routed sink.

Created on Nov 25, 2017

@author: aevans
'''

from thespian.actors import ActorTypeDispatcher
from reactive.message.stream_messages import Push, Pull
from concurrent.futures.thread import ThreadPoolExecutor
from multiprocessing import cpu_count
from reactive.structures.thread_queue import ReactiveQueue
from atomos.atomic import AtomicInteger
from threading import Lock


class SinkActor(ActorTypeDispatcher):

    def __init__(self):
        super(SinkActor, self).__init__()
        self.__fill_perc = 0.5
        self.__default_q_size = 1000
        self.__work_q = ReactiveQueue(maxsize=1000)
        self.__max_batch_size = 100
        self.__max_conc = cpu_count()
        self.__is_started = False
        self.__hlock = Lock()
        self.__req_out = AtomicInteger(0)
        self.__tpool = ThreadPoolExecutor(self.__max_conc)

    def receiveMsg_SetDefaultQueueFillRate(self, msg, sender):
        """
        Reset the default queue fill rate.

        :param msg:  The message with the int payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__fill_perc = msg.payload

    def receiveMsg_SetMaxBatchRequestSize(self, msg, sender):
        """
        Reset the max batch request size

        :param msg:  The message with the int payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_size = msg.payload

    def receiveMsg_SetConcurrency(self, msg, sender):
        """
        Handle a request to set the concurrency level.  This must be done
        before registering the actor with the sink supervisor. 

        :param msg:  The message with the int payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if not self.__is_started:
            self.__max_conc = msg.payload
            self.__tpool = ThreadPoolExecutor(self.__max_conc)
        

    def on_done_callback(self, fut):
        """
        Callback for handling final processing.

        :param fut:  The future being completed
        :type fut:  Future
        """
        try:
            sz, msg, sender = fut.result(10)
            qperc = self.__default_q_size * self.__fill_perc 
            qfill = self.__work_q.qsize()
            if qfill <= qperc:
                pll = Pull(self.__max_batch_size, sender, self.myAddress)
                self.send(sender, msg)
            else:
                msg = Push(None, self, sender)
        finally:
            with self.__hlock:
                self.__req_out.get_and_subtract(1)

    def do_push(self, batch, msg, sender):
        """
        User overwritten class that handles the push.

        :param batch:  The batch to handle
        :type batch:  list
        :param msg:  The message to handle with the batch payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        pass

    def handle_push(self, msg, sender):
        """
        Handle a push and return the pullsize in the future.

        :param msg:  The message to handle with the batch payload
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch = msg.payload
        self.do_push(batch, msg, sender)
        if isinstance(batch, list):
            return [len(batch), msg, sender]
        else:
            return [1, msg, sender]

    def receiveMsg_Push(self, msg, sender):
        """
        Handle a push to the sink.

        :param msg:  The message to push
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        batch = msg.payload
        if isinstance(batch, list):
            self.__work_q.put_all_nowait(batch)
            batch = self.__work_q.get_n_nowait(self.__max_batch_size)
            while len(batch) > 0:
                fut = self.__tpool.submit(self.do_push, batch, msg, sender)
                fut.add_done_callback(self.on_done_callback)
                self.__req_out.get_and_add(1)
                mbs = self.__req_out.get() * self.__max_batch_size
                if  mbs > self.__default_q_size:
                    batch = []
                else:
                    batch = self.__work_q.get_n_nowait(self.__max_batch_size)
