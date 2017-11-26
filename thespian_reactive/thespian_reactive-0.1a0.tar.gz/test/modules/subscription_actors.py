'''
Test objects for creating a stream.

Created on Nov 6, 2017

@author: aevans
'''

from reactive.actor.base_actor import BaseActor


class WorkerTest(BaseActor):

    def __init__(self):
        super().__init__()


class PubTestActor(BaseActor):

    def __init__(self):
        super().__init__()
