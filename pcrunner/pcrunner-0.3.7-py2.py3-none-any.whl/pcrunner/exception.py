#!/usr/bin/env python
# -*- coding: utf-8 -*-
# vim: ts=4 et sw=4 sts=4 ft=python fenc=UTF-8 ai

'''
pcrunner.exceptions
-----------------------

All exceptions used in the PassiveCheckRunner code base are defined here.

'''


class PassiveCheckRunnerException(Exception):
    '''
    Base exception class. All PassiveCheckRunner specific exceptions should
    subclass this class.
    '''


class PostFailed(PassiveCheckRunnerException):
    '''
    Raised when an error occurs when posting results:
        * An error occurs while posting.
        * A non 200 HTTP return code.
    '''


class PostResultTooBig(PassiveCheckRunnerException):
    '''
    Raised when post result are bigger then max_post_size.
    '''
