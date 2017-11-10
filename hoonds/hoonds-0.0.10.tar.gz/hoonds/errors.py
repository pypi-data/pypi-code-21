#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
.. currentmodule:: exceptions
.. moduleauthor:: Pat Daburu <pat@daburu.net>

This module defines common exceptions and other helpful error-handling tools.
"""

from abc import ABCMeta


class CustomException(Exception):
    __metaclass__ = ABCMeta

    """
    Extend this class to create a custom exception.
    """
    def __init__(self, message: str, inner: Exception=None):
        """

        :param message: the exception message
        :param inner: the exception that caused this exception
        """
        super().__init__(message)
        self._message: str = message
        self._inner: Exception = inner

    @property
    def message(self) -> str:
        """
        Get the exception message.
        :return: the exception message
        """
        return self._message

    @property
    def inner(self) -> Exception:
        """
        Get the inner exception that caused this exception.
        :return: the inner exception
        """
        return self._inner
