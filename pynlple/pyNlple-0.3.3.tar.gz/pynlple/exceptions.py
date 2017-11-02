# -*- coding: utf-8 -*-


class NLException(Exception):

    def __init__(self, message):
        message = '[' + self.__class__.__name__ + ']: ' + message
        super().__init__(message)

class TokenizationException(NLException):
    pass

class DataSourceException(NLException):
    pass
