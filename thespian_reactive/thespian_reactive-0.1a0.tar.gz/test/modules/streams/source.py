'''
String source.

Created on Nov 12, 2017

@author: aevans
'''

from reactive.streams.objects.basic_source import BasicSource


class StringTestSource(BasicSource):

    def __init__(self):
        super().__init__()
        self.__index = 0

    def do_pull(self, batch_size, msg, sender):
        batch = []
        for i in range(0, batch_size):
            self.__index += 1
            str = "Pull # {}".format(self.__index)
            batch.append(str)
        return batch
