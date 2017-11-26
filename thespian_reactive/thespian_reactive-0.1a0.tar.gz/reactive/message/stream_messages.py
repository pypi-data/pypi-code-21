'''
Messages associated with streams in general.

Created on Oct 30, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class Start(Message):
    """
    Start the stream
    """
    pass


class SetConcurrency(Message):
    """
    Set the maximum concurrency level.
    """
    pass


class SetRabbitExchange(Message):
    """
    Set the Rabbit MQ Exchange
    """

    def __init__(self, payload, key, host, port, target, sender):
        """
        Constructor

        :param payload:  The exchange name
        :type payload :  str
        :param key:  The routing key
        :type key:  str
        :param host:  The queue host
        :type host:  str
        :param port:  The connection port
        :type port:  int
        :param target:  The message target
        :type target:  BaseActor
        :param sender:  The message sender
        :type sender:  BaseActor
        """
        super().__init__(payload, target, sender)
        self.key = key
        self.host = host
        self.port = port

class GetStatisticsViaRabbitMQ(Message):
    """
    Call the statistics method which releases statistics back to the rabbit mq
    queue.
    """
    pass

class Peek(Message):
    """
    A peek request for test.
    """
    pass


class TearDown(Message):
    """
    A TearDown message sent to cancel components in a stream.
    """
    pass


class SetDropPolicy(Message):
    """
    Set the drop policy per the enumeration.  The payload is the enumeration
    value.
    """
    pass


class GetDropPolicy(Message):
    """
    Get the drop policy.  This policy is used when the buffers become full.
    """
    pass


class Pull(Message):
    """
    Send a pull request for obtaining batch results.  The payload is the batch
    size.
    """
    pass


class Push(Message):
    """
    Push batch results to a stream component. Payload is the list of results.
    """
    pass


class Complete(Message):
    """
    Send a message to signal completion of a component.  Payload varies.
    """
    pass


class Cancel(Message):
    """
    Cancel a stream component.  This calls the cancel method.  Payload ignored.
    """
    pass


class SetPublisher(Message):
    """
    Set the publisher of a message.  Payload is the publisher.
    """
    pass


class GetPublisher(Message):
    """
    Get the publisher.  Payload is generally ignored.
    """
    pass


class PullWithRequester(Message):
    """
    Send a pull request with the requestor attached to avoid intermediate steps.
    """

    def __init__(self, payload, requestor, target, sender):
        """
        Constructor

        :param payload:  The batch size to pull
        :type payload:  int()
        :param requestor:  The requestor / actor to send a response to.
        :type requestor:  BaseActor
        :param target:  The target actor for the message
        :type target:  Base Actor
        :param sender:  The actual message sender
        :type sender:  BaseActor
        """
        super().__init__(payload, target, sender)
        self.requestor = requestor


class RegisterKlass(Message):
    """
    Register a class with an actor.  Payload is the class object.
    """
    pass


class SetMinBatchSize(Message):
    """
    Set the minimum batch size to work with.  Payload is the batch size int.
    """
    pass


class SetMinBatchWaitTimes(Message):
    """
    Set the minimum times to wait for the minimum batch size to be reached.
    Payload is the minimum batch size int.
    """
    pass


class SetDefaultQueueFillRate(Message):
    """
    Set the default queue fill rate.  
    """
    pass


class SetMaxPullWaitTime(Message):
    """
    Set the maximum time to wait between pulls.  Payload is int.  Time is
    typically in seconds.
    """
    pass


class SetMaxBatchRequestSize(Message):
    """
    Set the maximum batch request size.  Payload is typically an int
    """
    pass
