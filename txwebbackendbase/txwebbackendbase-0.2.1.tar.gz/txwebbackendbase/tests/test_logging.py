# -*- coding: utf-8 -*-
"""
test_logging
----------------------------------
Tests for `logging` module.
"""
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import logging

from txwebbackendbase.logging import setupLogger

log = logging.getLogger(__name__)


class TestLogging(object):
    def test_something(self):
        setupLogger(level=logging.DEBUG)
        log.debug("debug mesg 1")
        setupLogger(level=logging.INFO)
        log.debug("debug mesg 2")
        log.info("info mesg")


if __name__ == '__main__':
    setupLogger(level=logging.DEBUG)
    log.debug("debug mesg 1")
    setupLogger(level=logging.INFO)
    log.debug("debug mesg 2 (should not be displayed)")
    log.info("info mesg 1 (should appear once)")
