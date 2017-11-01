#!/usr/bin/env python
# -*- coding: utf-8 -*-
# File: debug_logger.py
# Author: Jimin Huang <huangjimin@whu.edu.cn>
# Date: 13.09.2017
import logging


class MockLoggingHandler(logging.Handler):
    """Mock logging handler to check for expected logs.

    Messages are available from an instance's ``messages`` dict, in order,
    indexed by a lowercase log level string (e.g., 'debug', 'info', etc.).
    """
    def __init__(self, *args, **kwargs):
        self.messages = {
            'debug': [], 'info': [], 'warning': [], 'error': [], 'critical': []
        }
        super(MockLoggingHandler, self).__init__(*args, **kwargs)

    def emit(self, record):
        """Store a message from ``record`` in the ``messages`` dict.

        Args:
            record: a ``LogRecord`` instance
        """
        self.acquire()
        try:
            self.messages[record.levelname.lower()].append(record.getMessage())
        finally:
            self.release()

    def reset(self):
        """Clear all messages from instance
        """
        self.acquire()
        try:
            self.messages = {
                'debug': [], 'info': [], 'warning': [], 'error': [],
                'critical': []
            }
        finally:
            self.release()
