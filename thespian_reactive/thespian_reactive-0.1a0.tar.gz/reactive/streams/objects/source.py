'''
A basic source class inherited by source methods.  This encapsulates basic
methods.

Created on Nov 18, 2017

@author: aevans
'''

import json
import pika
from reactive.error.handler import handle_actor_system_fail
from reactive.message.stream_messages import TearDown, GetStatisticsViaRabbitMQ,\
    SetRabbitExchange
import sys
from random import Random


class SourceBase:

    def setup(self):
        """
        Constructor
        """
        self.__rabbit_exchange = None
        self.__rabbit_routing_key = None
        self.__connection = None
        self.__channel = None
        self.__host = None
        self.__port = 5000 + int(Random().random() * 15000)
        self.__pulls = 0
        self.__pushes = 0
        self.__errors = 0

    def increment_errors(self):
        """
        Increment errors.
        """
        self.__errors += 1
        if self.__errors == sys.maxsize:
            self.__errors = 0

    def increment_pull(self):
        """
        Called on a pull to increment the pull statistic.
        """
        self.__pulls += 1
        if self.__pulls is sys.maxsize:
            self.__pulls = 0

    def increment_push(self):
        """
        Called on a push to increment the push.
        """
        self.__pushes += 1
        if self.__pushes is sys.maxsize:
            self.__pushes = 0

    def handle_teardown(self, msg, sender):
        """
        Handle Source teardown.
        """
        if self.__channel:
            self.__channel.close()
            self.__connection.close()

    def open_rabbit_channel(self, msg, sender):
        """
        Open a rabbit mq channel.

        :param msg:  The message to handle
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        if self.__channel:
            self.__channel.close()
        self.__rabbit_exchange = msg.payload
        self.__host = msg.host
        self.__port = msg.port
        self.__rabbit_routing_key = msg.key
        pars = None
        if self.__port:
            pars = pika.ConnectionParameters(self.__host, port=self.__port)
        else:
            pars = pika.ConnectionParameters(self.__host)
        self.__connection = pika.BlockingConnection(pars)
        self.__channel = self.__connection.channel()
        self.__channel.queue_declare(queue=self.__rabbit_routing_key)

    def get_statistics(self, msg, sender):
        """
        Get statistics from this class.

        :param msg:  The message
        :type msg:  Message
        :param sender:  The message sender
        :type sender:  BaseActor
        :param actor:  The actor to use
        :type actor:  BaseActor
        """
        if self.__rabbit_exchange is not None:
            jdict = {
                "actor" : str(msg.target),
                "pulls" : self.__pulls,
                "pushes" : self.__pushes,
                "errors" : self.__errors
            }
            jstr = json.dumps(jdict)
            self.__channel.basic_publish(exchange=self.__rabbit_exchange,
                                         routing_key=self.__rabbit_routing_key,
                                         body=jstr)

    def handle_message(self, msg, sender):
        """
        Handle a message when multiple objects are extended.
        Sources tend to also be publishers.

        :param msg:  Message to handle
        :type msg:  Message
        :param sender:  Message sender
        :type sender:  BaseActor
        """
        try:
            if isinstance(msg, TearDown):
                self.handle_teardown(msg, sender)
            elif isinstance(msg, GetStatisticsViaRabbitMQ):
                self.get_statistics(msg, sender)
            elif isinstance(msg, SetRabbitExchange):
                self.open_rabbit_channel(msg, sender)
        except Exception:
            handle_actor_system_fail()
            self.__errors += 1
