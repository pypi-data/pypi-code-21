'''
Messages specific to stream sinks.

Created on Nov 25, 2017

@author: aevans
'''

from reactive.message.base_message import Message


class Start(Message):
    """
    Start the sink, should propogate up the stream.
    """
    pass


class GetIdleTime(Message):
    """
    Get the idle time for the sink.
    """
    pass


class GetLastPushTime(Message):
    """
    Get the last push time.
    """
    pass
