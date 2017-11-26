'''
A graph manager actor for the supervision pattern.  This allows the stream
actors to be monitored and failures to be handled appropriately.

Created on Nov 12, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor


class Manager(BaseActor):

    def __init__(self):
        super().__init__()

    def handle_child_exit(self):
        pass
