'''
Graph stage configuration objects.  The configs assume that graphs are being
created left to right.

Created on Nov 24, 2017

@author: aevans
'''


class GraphStageSettings:

    def __init__(self, concurrency, max_batch_size, drop_policy, sub_pool_type,
                 publisher_type):
        self.concurrency = concurrency
        self.max_batch_size = max_batch_size
        self.drop_policy = drop_policy
        self.sub_pool_type = sub_pool_type
        self.publisher_type = publisher_type


class GraphStageNode:

    def __init__(self, subscriptions, stage, settings):
        self.subscriptions = subscriptions
        self.stage = stage
        self.settings  = settings
        self.sub_pool = None
        self.stage = None
        self.publisher = None
