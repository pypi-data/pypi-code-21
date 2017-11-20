#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.exceptions
    ~~~~~~~~~~~~

    This module contains the set of Agent' exceptions.

    :copyright: (c) 2017 by Ma Fei.
"""
import json


class AgentException(Exception):
    """A agent error occurred."""


class GracefulExitException(Exception):
    """A exit error occurred."""


class WorkerException(AgentException):
    """A worker error occurred."""


class FTPException(AgentException):
    """A ftp error occurred."""


try:
    FileNotFoundError = FileNotFoundError
except NameError:
    FileNotFoundError = IOError

try:
    JSONDecodeError = json.decoder.JSONDecodeError
except AttributeError:
    JSONDecodeError = ValueError


class MyBaseError(BaseException):
    pass


class FileFormatError(MyBaseError):
    pass


class ParamsError(MyBaseError):
    pass


class ResponseError(MyBaseError):
    pass


class ParseResponseError(MyBaseError):
    pass


class ValidationError(MyBaseError):
    pass


class NotFoundError(MyBaseError):
    pass


class FunctionNotFound(NotFoundError):
    pass


class VariableNotFound(NotFoundError):
    pass


class ApiNotFound(NotFoundError):
    pass


class SuiteNotFound(NotFoundError):
    pass


class TestcaseNotFound(NotFoundError):
    pass
