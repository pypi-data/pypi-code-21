'''
A stream source serving the pull method.

Created on Nov 17, 2017

@author: aevans
'''

from reactive.streams.objects.source_actor import SourceActor
from reactive.message.stream_messages import Push


class StringSource(SourceActor):

    def __init__(self):
        super().__init__()
        self.__index = 0

    def do_pull(self, msg, sender):
        if msg.sender:
            sender = msg.sender
        batch_size = msg.payload
        batch = []
        for i in range(0, batch_size):
            self.__index += 1
            rval = "Pull {}".format(self.__index)
            batch.append(rval)
        msg = Push(batch, sender, self)
        self.send(sender, msg)
