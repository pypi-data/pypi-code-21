'''
Source configuration for the graph.

Created on Nov 24, 2017

@author: aevans
'''

class GraphSourceSettings:

    def __init__(self, publisher_type):
        self.publisher_type = publisher_type

class GraphSourceNode:

    def __init__(self, source, settings):
        self.source = source
        self.settings = settings
