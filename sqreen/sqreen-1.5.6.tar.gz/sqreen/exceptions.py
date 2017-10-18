# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Sqreen exceptions
"""


class SqreenException(Exception):
    """ Base exception for all sqreen exceptions
    """

    def __str__(self):
        return self.__repr__()

    def exception_infos(self):
        return {}


class InvalidArgument(SqreenException):
    """ Exception raised when sqreen code receive invalid arguments like bad
    rule dict.
    """
    pass


# This exception name is particularly important since it is often seen by
# Sqreen users when watching their logs. It should not raise any concern to
# them.
class AttackBlocked(SqreenException):
    """ Raised when a callback detected an attack
    """

    def __init__(self, rule_name):
        self.rule_name = rule_name

    def __repr__(self):
        msg = "Sqreen blocked a security threat (type: #{}). No action is required."
        return msg.format(self.rule_name)

###
# HTTP Exceptions
###


class SqreenHttpException(SqreenException):
    pass


class InvalidResponseContentType(SqreenHttpException):

    def __init__(self, content_type):
        self.content_type = content_type

    def __repr__(self):
        return 'Invalid response Content-Type: {!r}'.format(self.content_type)


class InvalidJsonResponse(SqreenHttpException):

    def __init__(self, parsing_exception):
        self.parsing_exception = parsing_exception

    def __repr__(self):
        msg = 'An error occured while trying to parse the response: {!r}'
        return msg.format(self.parsing_exception)


class StatusFailedResponse(SqreenHttpException):

    def __init__(self, response):
        self.response = response

    def __repr__(self):
        msg = 'Response returned with a status false: {!r}'
        return msg.format(self.response)


class InvalidStatusCodeResponse(SqreenHttpException):

    def __init__(self, status, response_data=None):
        self.status = status
        self.response_data = response_data

    def __repr__(self):
        msg = 'Response status code is invalid: {!r}'
        return msg.format(self.status)


# Incompotible exceptions that may be raised at startup


class UnsupportedFrameworkVersion(Exception):

    def __init__(self, framework, version):
        self.framework = framework
        self.version = version

    def __str__(self):
        return "{} in version {} is not supported".format(self.framework.title(), self.version)


class UnsupportedPythonVersion(Exception):

    def __init__(self, python_version):
        self.python_version = python_version

    def __str__(self):
        return "Python version {} is unsupported".format(self.python_version)
