#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    agent.exceptions
    ~~~~~~~~~~~~

    This module contains the set of Agent' exceptions.

    :copyright: (c) 2017 by Ma Fei.
"""


class AgentException(Exception):
    """A agent error occurred."""


class GracefulExitException(Exception):
    """A exit error occurred."""


class WorkerException(AgentException):
    """A worker error occurred."""


class FTPException(AgentException):
    """A ftp error occurred."""
