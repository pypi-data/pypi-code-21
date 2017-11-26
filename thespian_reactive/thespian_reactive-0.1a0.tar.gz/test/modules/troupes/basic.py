'''
Basic Troupe Test Actor which acts like a ping-pong actor, sending confirmation
back to the sender.

The max_count (max actors) and idle_count (min actors) are optional.

Created on Nov 20, 2017

@author: aevans
'''

from thespian.troupe import troupe
from multiprocessing import cpu_count
from reactive.streams.actors.troupe import TroupeStageBase
import pdb


@troupe(max_count=cpu_count(), idle_count=1)
class TroupeTestActor(TroupeStageBase):

    def __init__(self):
        super().__init__()
        self.__index = 0

    def do_work(self, batch):
        if isinstance(batch, list):
            obatch = []
            for i in range(0, len(batch)):
                rval = "Push Number {}".format(i)
                obatch.append(rval)
            return obatch
        else:
            return batch
