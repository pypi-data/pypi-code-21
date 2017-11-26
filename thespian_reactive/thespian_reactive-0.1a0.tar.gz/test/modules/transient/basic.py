"""
Basic transient actor for testing.

Created Nov 22, 2017

@author: aevans
"""

from thespian.transient import transient_idle
from reactive.streams.actors.transient import TransientStageBase
from datetime import timedelta


@transient_idle(timedelta(seconds=120))
class TransientTestActor(TransientStageBase):

    def __init__(self):
        super().__init__()

    def do_work(self, batch):
        """
        Perform fake work.

        :param batch:  The work batch
        :type batch:  list
        """
        obatch = []
        if isinstance(batch, list):
            for res in batch:
                rstr = "Pull {}".format(res)
                obatch.append(rstr)
        return obatch
