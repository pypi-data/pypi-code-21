'''
The transient stage supervisor uses transient actors to maintain a dynamic
set of actors to perform work.  Max and min router size is specifiable.
Actors are added to a router and submitted to the transient actor through this
supervisor.  The transient should send messages back to the publisher which is
used as the sender in the message.

This supervisor relies on a triangular type routing pattern.  The publisher 
requests work from the supervisor which pushes work to the transient actor.
The transient actor sends any completed work back to the publisher.

The transient actors maintain contact with the subscription pool.  This is registered
on startup.

The subscription pool needs to be registered with this supervisor as does the transient
actor class. Max and min actor counts and other settings should be set through the
TransientStageSettings message.

Created on Nov 21, 2017

@author: aevans
'''

from thespian.actors import ActorTypeDispatcher, ChildActorExited
from multiprocessing import cpu_count
from reactive.routers.router_type import RouterType
from reactive.routers.round_robin import RoundRobinRouter
from reactive.routers.random import RandomRouter
from reactive.message.stream_work_stage_messages import SetSubscriptionPool,\
    GetActorStatistics
from reactive.message.stream_messages import Pull, TearDown
from reactive.message.router_messages import Subscribe, DeSubscribe, RouteTell
from _datetime import datetime
from scipy.stats import poisson


class TransientStageSupervisor(ActorTypeDispatcher):

    def __init__(self):
        """
        Constructor
        """
        super().__init__()
        self.__last_pull_time = datetime.now()
        self.__max_pull_time = 60
        self.__pull = 0
        self.__pps = []
        self.__router_actors = []
        self.__klass = None
        self.__min_count = 1
        self.__max_count = cpu_count()
        self.__router_type = RouterType.ROUND_ROBIN
        self.__router = None
        self.__sub_pool = None

    def receiveMsg_SetHeartbeatInterval(self, msg, sender):
        """
        Set the maximum heartbeat interval to use before checking the
        distribution.  Restarts the actors and resets the pull time queue
        as well.

        :param msg:  The message containing the int interval
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__max_pull_time = msg.payload
        self.__pps = []
        to_start = self.__max_count - len(self.__router_actors)
        self.create_router_actors(to_start)

    def receiveMsg_GetActorStatistics(self, msg, sender):
        """
        Obtain statistics from this actor.  Returns to sender.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  
        """
        if msg.sender:
            sender = msg.sender
        stats = {
            "actor" : str(self),
            "pulls" : self.__pull,
            "router_length": len(self.__router),
            "last_pull" : ""
        }
        
        if self.__last_pull_time:
            stats["last_pull"] = self.__last_pull_time.strftime(
                "%d-%M-%Y %H:%m:%s")
        msg = GetActorStatistics(stats, sender, self)
        self.send(sender, msg)

    def receiveMsg_TransientStageSettings(self, msg, sender):
        """
        Set settings in the TransientStageSupervisor

        :param msg:  The settings message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.router_type:
            self.__router_type = msg.router_type
        
        if msg.payload:
            self.__klass = msg.payload
            if self.__router is None:
                self.create_router()

    def create_router(self):
        """
        Create a router.
        """
        ractor = None
        if self.__router_type is RouterType.ROUND_ROBIN:
            ractor = RoundRobinRouter
        elif self.__router_type is RouterType.BROADCAST:
            ractor = RandomRouter
        elif self.__router_type is RouterType.RANDOM:
            ractor = RandomRouter
        self.__router = self.createActor(ractor)
        self.create_router_actors(self.__max_count)

    def create_router_actors(self, num_actors):
        """
        Create actors for the router.

        :param num_actors:  The number of actors to create
        :type num_actors:  int
        """
        if self.__klass:
            for i in range(0, num_actors):
                actr = self.createActor(self.__klass)
                msg = Subscribe(actr, self.__router, self.myAddress)
                self.send(self.__router, msg)
                msg = SetSubscriptionPool(self.__sub_pool, actr, self.myAddress)
                self.send(actr, msg)
                self.__router_actors.append(actr)

    def receiveMsg_TearDown(self, msg, sender):
        """
        Handle a tear down message.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        for router in self.__router_actors:
            msg = TearDown(None, msg, self.myAddress)
            self.send(router, msg)

    def receiveMsg_ChildActorExited(self, msg, sender):
        """
        Handle the child actor exited message to restart transient actors and
        routers.

        :param msg:  Message containing the exited actors address
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        addr = str(msg.childAddress)
        str_actors = [str(x) for x in self.__router_actors]
        if str(addr) == str(self.__router):
            for actr in self.__router_actors:
                self.send(actr, ChildActorExited())
            del self.__router_actors
            self.__router_actors = []
            self.create_router()
        elif str(addr) in str_actors:
            actr = self.__router_actors[str_actors.index(str(addr))]
            msg = DeSubscribe(actr, self.__router, self)
            self.send(self.__router, msg)
            self.__router_actors.remove(actr)

        if len(self.__router_actors) < self.__min_count:
            ct = self.__min_count - len(self.__router_actors)
            actr = self.create_router_actors(ct)

    def add_new_actor(self):
        """
        Handle the addition of another actor.
        """
        actr = self.createActor(self.__klass)
        msg = Subscribe(actr, self.__router, self)
        self.send(self.__router, msg)

    def receiveMsg_SetSubscriptionPool(self, msg, sender):
        """
        Set the subscription pool for the actors.

        :param msg:  The message containing the pool
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        self.__sub_pool = msg.payload
        for actr in self.__router_actors:
            msg = SetSubscriptionPool(self.__sub_pool, actr, self)
            self.send(actr, msg)

    def receiveMsg_Pull(self, msg, sender):
        """
        Handle a pull request from the publisher.

        :param msg:  The message containing the pool
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if msg.sender:
            sender = msg.sender
        if self.__router is None:
            self.create_router()
        msg = Pull(msg.payload, self.__router, sender)
        msg = RouteTell(msg, self.__router, sender)
        self.send(self.__router, msg)
        dt = datetime.now()
        dt = dt - self.__last_pull_time
        if dt.total_seconds() > self.__max_pull_time:
            self.check_increase()

    def check_increase(self):
        """
        Check and increase the number of router actors if necessary.
        """
        if len(self.__pps) > 5:
            mu = sum(self.__pps)
            mu = mu / len(self.__pps)
            perc = poisson.cdf(self.__pull, mu)
            if perc > .63:
                create_count = self.__max_count - len(self.__router_actors)
                self.create_router_actors(create_count)
                self.__pps = self.__pps[-1:]
                self.__pull = 1
            if len(self.__pps) > 100:
                self.__pps.pop(0)
            self.__pps.append(self.__pull)
            self.__last_pull_time = datetime.now()
