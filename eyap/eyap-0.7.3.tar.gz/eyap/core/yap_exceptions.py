"""Module to collect exceptions we might throw.
"""

class UnableToFindUniqueTopic(Exception):

    def __init__(self, topic, count, extra):
        msg = 'Unable to find unique thread for topic %s. Found %i items. %s'%(
            topic, count, extra)
        Exception.__init__(self, msg)
