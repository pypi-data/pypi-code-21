'''
Stream related errors that a user may wish to use.

Created on Oct 31, 2017

@author: aevans
'''


class SourceError(Exception):
    """
    Errors from the source.
    """

    def __init__(self, message):
        super(SourceError, self).__init__(message)


class ProcessNodeError(Exception):
    """
    Errors from a processor.
    """

    def __init__(self, message):
        super(ProcessNodeError, self).__init__(message)


class RouterNodeError(Exception):
    """
    Errors from a router.
    """
    def __init__(self, message):
        super(RouterNodeError, self).__init__(message)


class SinkError(Exception):
    """
    Errors from a sink.
    """
    def __init__(self, message):
        super(SinkError, self).__init__(message)
