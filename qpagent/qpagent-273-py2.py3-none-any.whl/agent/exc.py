#!/usr/bin/env python
# -*- coding: utf-8 -*-


class GracefulExitException(Exception):
    pass


class WorkerException(Exception):
    pass


class AgentException(Exception):
    pass


class FTPException(Exception):
    pass
