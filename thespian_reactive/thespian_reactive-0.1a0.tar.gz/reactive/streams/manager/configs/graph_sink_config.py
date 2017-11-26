'''
Graph sink settings.

Created on Nov 24, 2017

@author: aevans
'''

class GraphSinkSettings:

    def __init__(self, subscription_type):
        self.subscription_type = subscription_type


class GraphSinkNode:

    def __init__(self, subscriptions, settings):
        self.subscriptions = subscriptions
        self.settings = settings
