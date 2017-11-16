#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from .pkg.loggerFactory import StreamOnlyLogger
except:
    from pytq.pkg.loggerFactory import StreamOnlyLogger


class ClassWithLogger(object):
    """
    A class with a built-in logger.
    """

    def __init__(self, logger=None, **kwargs):
        if logger is None:
            self.logger = StreamOnlyLogger()
        else:
            self.logger = logger
        self.verbose = True

    def log_on(self):
        """
        Turn on logger.
        """
        self.verbose = True
        self.logger.enable_verbose = True

    def log_off(self):
        """
        Turn off logger.
        """
        self.verbose = False
        self.logger.enable_verbose = False

    def debug(self, msg, indent=0):
        """
        Log a debug message.
        """
        if self.verbose:
            self.logger.debug(msg, indent)

    def info(self, msg, indent=0):
        """
        Log a info message.
        """
        if self.verbose:
            self.logger.info(msg, indent)

    def warning(self, msg, indent=0):
        """
        Log a warning message.
        """
        if self.verbose:
            self.logger.warning(msg, indent)

    def error(self, msg, indent=0):
        """
        Log a error message.
        """
        if self.verbose:
            self.logger.error(msg, indent)

    def critical(self, msg, indent=0):
        """
        Log a critical message.
        """
        if self.verbose:
            self.logger.critical(msg, indent)

    def show(self, msg, indent=0):
        """
        Print to console.
        """
        self.logger.show(msg, indent=indent)
