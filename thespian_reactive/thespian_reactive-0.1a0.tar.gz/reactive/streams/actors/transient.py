'''
An actor for the general stage.  This stage runs in a separate process. Each 
stage uses its own dedicated process pool with a configurable concurrency
level.

Created on Nov 21, 2017

@author: aevans
'''

from multiprocessing import Process, Value, Lock
from thespian.actors import ActorTypeDispatcher
from reactive.structures.proc_queue import ReactiveMutliProcessingQueue
from reactive.message.stream_messages import Push, Pull
from reactive.message.stream_work_stage_messages import GetActorStatistics
import sys
import multiprocessing
from ctypes import c_bool


class TransientStageBase(ActorTypeDispatcher):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        
        # basic vars
        self.__term_lock = Lock()
        self.__terminating = Value(c_bool, False)
        self.__pulls = 0
        self.__pushes = 0
        self.__req_count = 0
        self.__sub_actor = None
        self.__is_empty_pull = False
        self.__default_q_size = 1000
        self.__fill_perc = .5
        self.__max_batch_request_size = 100
        self.__drop_policy = "ignore"
        self.ctx = multiprocessing.get_context(self.get_ctx_type())
        self.__result_q = ReactiveMutliProcessingQueue(
            maxsize=self.__default_q_size, ctx=self.ctx)
        self.__work_q = ReactiveMutliProcessingQueue(
            maxsize=self.__default_q_size, ctx=self.ctx)
        self.__restart_worker = True

        # kickstart procs
        self.__max_conc = 1
        self.__process_pool = []
        self.create_workers()

    def get_ctx_type(self):
        """
        Get the context type using the platform

        :return:  The context type
        :rtype:  str
        """
        platform = sys.platform
        if platform == "linux" or platform == "linux2":
            self.ctx = multiprocessing.get_context("fork")
        else:
            self.ctx  = multiprocessing.get_context("spawn")

    def receiveMsg_TearDown(self, msg, sender):
        """
        Handle the message receipt.

        :param message:  The TearDown message
        :type message:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        with self.__term_lock:
            self.__terminating.value = True
        try:
            if self.__process_pool:
                for proc in self.__process_pool:
                    try:
                        proc.join()
                        del proc
                    except:
                        pass
        finally:
            self.__work_q.close()
            self.__result_q.close()

    def receiveMsg_SetConcurrency(self, msg, sender):
        """
        Set the concurrency.  Resets pool.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_conc = msg.payload
        self.create_workers()

    def clean_process_pool(self):
        """
        Remove processes from the pool if they are not active.
        """
        self.__process_pool = [
            x for x in self.__process_pool if x.is_alive() is False]

    def create_workers(self):
        """
        Create the workers in the producer consumer pattern this
        stage utilizes
        """
        if len(self.__process_pool) > self.__max_conc:
            kill_ct = len(self.__process_pool) - self.__max_conc
            for i in range(0, kill_ct):
                prc = self.__process_pool.pop(0)
                try:
                    prc.terminate()
                    prc.join()
                    del prc
                except:
                    pass
        else:
            for i in range(0, self.__max_conc):
                proc = Process(target=self.handle_worker,
                    args=(self.__work_q, self.__result_q,
                    self.__drop_policy, self.do_work,
                    self.__max_batch_request_size, self.__term_lock,
                    self.__terminating))
                proc.start()
                self.__process_pool.append(proc)

    def do_work(self, batch):
        """
        Handle a workload.

        :param batch:  The batch to handle
        :type batch:  list
        """
        return []

    def handle_worker(self, work_q, result_q, drop_policy, work_func,
                      max_batch, tlock, tval):
        """
        Handle the future on finish.

        :param work_q:  Worker queue
        :type work_q:  Queue
        :param result_q:  Result queue
        :type result_q:  Queue
        :param drop_policy:  The drop policy
        :type drop_policy:  str
        :param work_func:  The work function
        :type work_func:  method or functions
        """
        with tlock:
            term = tval.value
        while not term:
            try:
                batch = work_q.get_n(max_batch)
                if len(batch) > 0:
                    rval = work_func(batch)
                    if isinstance(rval, list):
                        result_q.put_all(rval)
                    else:
                        result_q.put(rval)
                with tlock:
                    term = tval.value
            except:
                pass

    def receiveMsg_GetActorStatistics(self, msg, sender):
        """
        Get statistics and send them back to the requestor.

        :param msg:  The actor message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        stats = {
            'pulls' : self.__pulls,
            'pushes' : self.__pushes
        }
        msg = GetActorStatistics(stats, sender, self.myAddress)
        self.send(sender, msg)

    def receiveMsg_SetSubscriptionPool(self, msg, sender):
        """
        Handle the subscription pool setting method.

        :param msg:  The message to handle with the BaseActor address
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__sub_actor = msg.payload

    def receiveMsg_SetDefaultQueueFillRate(self, msg, sender):
        """
        Set the default queue fill rate.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__fill_perc = msg.payload

    def receiveMsg_SetMaxBatchRequestSize(self, msg, sender):
        """
        Set the maximum batch request size.

        :param msg:  The message to handle with the int batch
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_batch_request_size = msg.payload

    def receiveMsg_SetDropPolicy(self, msg, sender):
        """
        Set the drop policy for the actor.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__drop_policy = msg.payload

    def check_pull(self):
        """
        Check whether a pull request must be made on the queue.
        """
        qperc = self.__fill_perc * self.__default_q_size
        qfill = self.__work_q.qsize()
        reqout = self.__req_count * self.__max_batch_request_size
        if qfill < qperc and reqout < self.__default_q_size:
            rsize = self.__default_q_size - self.__result_q.qsize()
            if rsize > 0:
                pull_size = self.__default_q_size - qfill
                pull_size = min([self.__max_batch_request_size, pull_size])
                pull_size = min([rsize, pull_size])
                msg = Pull(pull_size, self.__sub_actor, self.myAddress)
                self.send(self.__sub_actor, msg)
                self.__req_count += 1

    def receiveMsg_Pull(self, msg, sender):
        """
        Handle the pull message.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        batch = []
        if self.__terminating.value is False:
            if self.__pulls < sys.maxsize:
                self.__pulls += 1
            if msg.sender:
                sender = msg.sender
            batch_size = msg.payload
            if self.__result_q.empty() is False:
                batch = self.__result_q.get_n_nowait(batch_size)
        msg = Push(batch, sender, self.myAddress)
        self.send(sender, msg)
        self.check_pull()

    def receiveMsg_Push(self, msg, sender):
        """
        Handle the push message.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if self.__terminating.value is False:
            if self.__pushes < sys.maxsize:
                self.__pushes += 1
            self.__req_count -= 1
            batch = msg.payload
            if isinstance(batch, list):
                if len(batch) > 0:
                    self.__is_empty_pull = False
                    batch = self.__work_q.put_all(batch)
                    if len(batch) > 0 and self.__drop_policy == "pop":
                        for res in batch:
                            try:
                                if self.__work_q.full():
                                    self.__work_q.get_nowait()
                                self.__work_q.put(res)
                            except:
                                pass
                else:
                    self.__is_empty_pull = True

            if self.__is_empty_pull is False:
                self.check_pull()
                
    def receiveMsg_RouteTell(self, msg, sender):
        """
        Handle a message sent through the router

        :param msg:  The message containing the wrapped Message
        :type msg:  Message
        :param sender:  The sender
        :type sender:  BaseActor  
        """
        msg = msg.payload
        self.receiveMsg_Pull(msg, sender)
