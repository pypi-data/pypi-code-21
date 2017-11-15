##############################################################################
#
# Copyright (c) 2004 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Tests for zope.app.server.accesslog.
"""
import logging
import unittest

from ZConfig.components.logger import loghandler

try:
    from ZConfig.components.logger.tests.test_logger import LoggingTestBase
except ImportError:
    from ZConfig.components.logger.tests.test_logger import LoggingTestHelper
    class LoggingTestBase(LoggingTestHelper, unittest.TestCase):
        pass

class TestAccessLogging(LoggingTestBase):

    name = "accesslog"

    _schematext = """
      <schema>
        <import package='zope.app.server' file='accesslog.xml'/>
        <section type='accesslog' name='*' attribute='accesslog'/>
      </schema>
    """

    def test_config_without_logger(self):
        conf = self.get_config("")
        self.assert_(conf.accesslog is None)

    def test_config_without_handlers(self):
        logger = self.check_simple_logger("<accesslog/>")
        # Make sure there's a NullHandler, since a warning gets
        # printed if there are no handlers:
        self.assertEqual(len(logger.handlers), 1)
        self.assert_(isinstance(logger.handlers[0],
                                loghandler.NullHandler))

    def test_formatter(self):
        logger = self.check_simple_logger("<accesslog>\n"
                                          "  <syslog>\n"
                                          "    level error\n"
                                          "    facility local3\n"
                                          "    format xyzzy\n"
                                          "  </syslog>\n"
                                          "</accesslog>")
        self.assertEqual(len(logger.handlers), 1)
        syslog = logger.handlers[0]
        self.assertEqual(syslog.level, logging.ERROR)
        self.assert_(isinstance(syslog, loghandler.SysLogHandler))
        self.assertEqual(syslog.formatter._fmt, "%(message)s")

    def check_simple_logger(self, text):
        conf = self.get_config(text)
        self.assert_(conf.accesslog is not None)
        logger = conf.accesslog()
        self.assert_(isinstance(logger, logging.Logger))
        self.assert_(not logger.propagate)
        self.assertEquals(logger.name, "accesslog")
        self.assertEquals(logger.level, logging.INFO)
        return logger
